# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models
import calendar, xlwt, base64
from datetime import datetime, timedelta
from collections import OrderedDict
from babel.numbers import format_decimal
from io import BytesIO


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_sale_vat_data(self, from_dt, to_dt, categ_id, product_id, shop_id):
        tz_new = self.env.user.tz
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d 00:00:00')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d 23:59:59')
        domain = f" (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date >= '{start_date}' AND (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        if shop_id:
            domain += " AND po.shop_id = (%s)" % (shop_id)
        SQL = f"""
                SELECT 
                    po.id as id,
                    TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'DD-MM-YYYY') as date_order,
                    po.name AS number,
                    (CASE WHEN (rp.name = '') IS NOT FALSE THEN rp.name ELSE '' END) AS customer_name,
                    rp.vat AS customer_tin,
                    pt.name as product,
                    uom.name as unit,
                    SUM(pol.qty) as qty, 
                    poc.name as categ_name,
                    ROUND(SUM(pol.price_subtotal), 3) as rate,
                    ROUND(SUM(pol.price_subtotal_incl - pol.price_subtotal), 3) as vat,
                    ROUND(SUM(pol.price_subtotal_incl), 3) as amount
                    FROM pos_order AS po
                    left join pos_order_line pol on pol.order_id = po.id
                    left join res_partner rp on po.partner_id = rp.id
                    left join product_product pp on pp.id = pol.product_id
                    left join product_template pt on pt.id = pp.product_tmpl_id
                    left join pos_category poc on poc.id = pt.pos_categ_id
                    left join uom_uom uom on uom.id = pol.uom_id
                WHERE {domain}
                GROUP BY po.date_order, po.id,
                po.name, pp.barcode, pt.name, uom.name, poc.name, rp.name, rp.vat
                ORDER BY TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'DD-MM-YYYY')
        """
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        for each in result:
            if not each.get('customer_name'):
                sql = f"""
                        SELECT 
                            aj.name as name, po.id as order
                            FROM pos_order AS po
                            left join account_bank_statement_line absl on absl.pos_statement_id = po.id
                            left join account_journal aj on absl.journal_id = aj.id
                        WHERE po.id = %s
                        GROUP BY po.id, aj.name 
                        LIMIT 1
                """ % each.get('id')
                self._cr.execute(sql)
                res = self._cr.dictfetchall()
                each['customer_name'] = res[0].get('name') if res else ''
        return result

    def export_as_pdf_report_sale_vat(self,from_dt, to_dt, categ_id, product_id, shop_id):

        data = self.get_sale_vat_data(from_dt, to_dt, categ_id, product_id, shop_id)
        d = from_dt + ' TO ' + to_dt
        rep_name = 'Sale VAT report'
        summary = {
            'report_name': rep_name,
            'data': d
        }
        report_id = self.env['report.sale.vat.wizard.download'].create({
            'name': 'Sale VAT report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'data_pdf': data,
            'summary': summary,
        })
        return report_id.id

    def export_as_excel_report_sale_vat(self, from_dt, to_dt, categ_id, product_id, shop_id):
        currency = self.env.user.company_id.currency_id.symbol
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Report')
        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        heading = xlwt.easyxf('font: bold on, height 300; align: horiz center;')
        bold = xlwt.easyxf('font: bold on;') or 'Non-Defined'
        bold1 = xlwt.easyxf('font: bold on;align: horiz right;')
        cell = xlwt.easyxf('align: horiz right;')
        cell1 = xlwt.easyxf('align: horiz left;')
        data = self.get_sale_vat_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            sheet.col(0).width = 256 * 15
            sheet.col(1).width = 256 * 20
            sheet.col(2).width = 256 * 15
            sheet.col(4).width = 256 * 10
            sheet.col(3).width = 256 * 50
            sheet.col(5).width = 256 * 10
            sheet.col(6).width = 256 * 15
            sheet.write_merge(0, 1, 0, 6, 'Sale VAT report', heading)
            i = 3
            g_tot_rate = g_tot_vat = g_tot_net_amt = 0
            sheet.write(i, 0, "Date", bold1)
            sheet.write(i, 1, "Invoice No.", bold)
            sheet.write(i, 2, "Customer", bold1)
            sheet.write(i, 3, "Customer TIN", bold1)
            sheet.write(i, 4, "Amount", bold1)
            sheet.write(i, 5, "Vat Amount", bold1)
            sheet.write(i, 6, "Total Amount", bold1)
            i = i + 1
            for d in data:
                tot_rate = 0
                tot_vat = 0
                tot_net_amt = 0
                sheet.write(i, 0, str(d.get('date_order')), cell1)
                sheet.write(i, 1, d.get('number'), cell1)
                sheet.write(i, 2, d.get('Customer'), cell1)
                sheet.write(i, 3, d.get('Customer TIN'), cell)

                sheet.write(i, 4, "%0.3f" % d.get('rate') + ' ' + currency, cell)
                tot_rate += float(d.get('rate'))
                g_tot_rate += float(d.get('rate'))
                sheet.write(i, 5, "%0.3f" % d.get('vat') + ' ' + currency, cell)
                tot_vat += float(d.get('vat'))
                g_tot_vat += float(d.get('vat'))
                sheet.write(i, 6, "%0.3f" % d.get('amount') + ' ' + currency, cell)
                tot_net_amt += float(d.get('amount'))
                g_tot_net_amt += float(d.get('amount'))
                i += 1
            sheet.write(i + 2, 0, 'Total', bold)
            sheet.write(i + 2, 1, '----', bold)
            sheet.write(i + 2, 2, '----', bold)
            sheet.write(i + 2, 3, '----', bold)
            sheet.write(i + 2, 4, "%0.3f" % g_tot_rate + ' ' + currency, bold1)
            sheet.write(i + 2, 5, "%0.3f" % g_tot_vat + ' ' + currency, bold1)
            sheet.write(i + 2, 6, "%0.3f" % g_tot_net_amt + ' ' + currency, bold1)
            sheet.write(i + 2, 7, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.sale.vat.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Sale VAT Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
