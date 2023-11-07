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

    def get_purchase_vat_data(self, from_dt, to_dt, categ_id, product_id):
        tz_new = self.env.user.tz
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d 00:00:00')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d 23:59:59')
        domain = f" po.state = 'purchase' AND (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date >= '{start_date}' AND po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}' <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        SQL = f"""
                    SELECT 
                        TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'DD-MM-YYYY') as date_order,
                        po.name AS number,
                        rp.name AS vendor_name,
                        rp.vat AS vendor_tin,
                        pt.name as product,
                        uom.name as unit,
                        pol.product_qty as qty, poc.name as categ_name,
                        ROUND(CAST(pol.price_subtotal as numeric), 3)::varchar as rate,
                        ROUND(CAST(pol.price_tax as numeric), 3)::varchar as vat,
                        ROUND(pol.price_total, 3)::varchar as amount
                        FROM purchase_order AS po
                        left join purchase_order_line pol on pol.order_id = po.id
                        left join res_partner rp on po.partner_id = rp.id
                        left join product_product pp on pp.id = pol.product_id
                        left join product_template pt on pt.id = pp.product_tmpl_id
                        left join pos_category poc on poc.id = pt.pos_categ_id
                        left join uom_uom uom on uom.id = pt.uom_id
                    WHERE {domain}
                    ORDER BY po.date_order
                    """
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        return result

    def export_as_pdf_report_purchase_vat(self,from_dt, to_dt, categ_id, product_id):

        data = self.get_purchase_vat_data(from_dt, to_dt, categ_id, product_id)

        d = from_dt + ' TO ' + to_dt

        rep_name = 'Purchase VAT report'
        summary = {
            'report_name': rep_name,
            'data': d
        }
        report_id = self.env['report.purchase.vat.wizard.download'].create({
            'name': 'Purchase VAT report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'data_pdf': data,
            'summary': summary,
        })
        return report_id.id

    def export_as_excel_report_purchase_vat(self, from_dt, to_dt, categ_id, product_id):
        currency = self.env.user.company_id.currency_id.symbol
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Report')
        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        heading = xlwt.easyxf('font: bold on, height 300; align: horiz center;')
        bold = xlwt.easyxf('font: bold on;')
        bold1 = xlwt.easyxf('font: bold on;align: horiz right;')
        cell = xlwt.easyxf('align: horiz right;')
        cell1 = xlwt.easyxf('align: horiz left;')
        data = self.get_purchase_vat_data(from_dt, to_dt, categ_id, product_id)
        if data:
            sheet.col(0).width = 256 * 15
            sheet.col(1).width = 256 * 20
            sheet.col(2).width = 256 * 15
            sheet.col(4).width = 256 * 10
            sheet.col(3).width = 256 * 50
            sheet.col(5).width = 256 * 10
            sheet.col(6).width = 256 * 15
            sheet.write_merge(0, 1, 0, 6, 'Purchase VAT report', heading)
            i = 3
            g_tot_rate = g_tot_vat = g_tot_net_amt = 0
            i = i + 2
            sheet.write(i, 0, "Date", bold)
            sheet.write(i, 1, "Purchase Invoice No.", bold)
            sheet.write_merge(i, i, 2, 3, "Vendor Name", bold)
            sheet.write_merge(i, i, 4, 5, "Vendor TIN", bold)
            sheet.write(i, 6, "Amount", bold1)
            sheet.write(i, 7, "Vat Amount", bold1)
            sheet.write(i, 8, "Total Amount", bold1)
            i = i + 1
            for d in data:
                sheet.write(i, 0, str(d.get('date_order')), cell1)
                sheet.write(i, 1, d.get('number'), cell1)
                sheet.write_merge(i, i, 2, 3, d.get('vendor_name'), cell1)
                sheet.write_merge(i, i, 4, 5, d.get('vendor_tin'), cell)
                sheet.write(i, 6, "%0.3f" % float(d.get('rate')) + ' ' + currency, cell)
                g_tot_rate += float(d.get('rate'))
                sheet.write(i, 7, "%0.3f" % float(d.get('vat')) + ' ' + currency, cell)
                g_tot_vat += float(d.get('vat'))
                sheet.write(i, 8, "%0.3f" % float(d.get('amount')) + ' ' + currency, cell)
                g_tot_net_amt += float(d.get('amount'))
                i += 1
            sheet.write(i + 2, 0, 'Total', bold)
            sheet.write(i + 2, 1, '----', bold)
            sheet.write(i + 2, 2, '----', bold)
            sheet.write(i + 2, 3, '----', bold)
            sheet.write(i + 2, 4, '----', bold)
            sheet.write(i + 2, 5, '----', bold)
            sheet.write(i + 2, 6, "%0.3f" % g_tot_rate + ' ' + currency, bold1)
            sheet.write(i + 2, 7, "%0.3f" % g_tot_vat + ' ' + currency, bold1)
            sheet.write(i + 2, 8, "%0.3f" % g_tot_net_amt + ' ' + currency, bold1)
            sheet.write(i + 2, 9, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.purchase.vat.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Purchase VAT Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: