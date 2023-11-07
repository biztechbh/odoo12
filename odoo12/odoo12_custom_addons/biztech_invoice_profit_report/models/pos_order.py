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

    def get_invoice_profit_data(self, from_dt, to_dt, categ_id, product_id):
        result_dict = {}
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d')

        domain = f" ai.date_invoice >= '{start_date}' AND ai.date_invoice <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND ail.product_id = (%s)" % (product_id)
        SQL = f'''
                select 
                    ai.date_invoice as invoice_date,
                    ai.number as invoice_number,
                    pp.barcode as barcode,
                    pp.id as product_id,
                    pt.name as product,
                    sum(ail.quantity) as qty,
                    poc.name as categ_name,
                    round(sum(ail.price_total), 3) as invoice_amount
                    from account_invoice_line as ail
                    left join account_invoice as ai on ai.id = ail.invoice_id
                    left join product_product pp on pp.id = ail.product_id
                    left join product_template pt on pt.id = pp.product_tmpl_id
                    left join pos_category poc on poc.id = pt.pos_categ_id
                    where {domain}
                    group by ai.date_invoice, 
                    ai.number, pp.barcode, pt.name, pp.id, poc.name
                    order by ai.date_invoice;
            '''
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        main_report_data = []
        for each in result:
            if each.get('categ_name') is None:
                each['categ_name'] = 'Non-Defined'
            each['categ_name'] = str(each.get('categ_name')).replace(' ', '_')
            cost_price = self.env['product.product'].browse(each.get('product_id')).standard_price
            each['cost'] = round((cost_price * each.get('qty')), 3)
            each['profit_amount'] = round(each.get('invoice_amount') - each.get('cost'), 3)
            each['profit_per'] = round((each.get('profit_amount') * 100) / (each.get('cost')), 2) if each.get('cost') != 0 else 100
            main_report_data.append(each)
        return main_report_data

    def export_as_pdf_report_invoice_profit(self,from_dt, to_dt, categ_id, product_id):

        data = self.get_invoice_profit_data(from_dt, to_dt, categ_id, product_id)

        d = from_dt + ' TO ' + to_dt

        rep_name = 'Invoice Profit report'
        summary = {
            'report_name': rep_name,
            'data': d
        }
        report_id = self.env['report.invoice.profit.wizard.download'].create({
            'name': 'Invoice Profit Report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'data_pdf': data,
            'summary': summary,
        })
        return report_id.id

    def export_as_excel_report_invoice_profit(self, from_dt, to_dt, categ_id, product_id):
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
        data = self.get_invoice_profit_data(from_dt, to_dt, categ_id, product_id)
        # data = sorted(data)
        if data:
            sheet.col(0).width = 256 * 15
            sheet.col(1).width = 256 * 15
            sheet.col(2).width = 256 * 15
            sheet.col(4).width = 256 * 15
            sheet.col(3).width = 256 * 20
            sheet.col(5).width = 256 * 15
            sheet.col(6).width = 256 * 20
            sheet.col(7).width = 256 * 20
            sheet.write_merge(0, 1, 0, 6, 'Invoice Profit Report', heading)
            i = 3
            g_tot_qty = g_tot_cost = g_tot_inv_amount = g_tot_profit = g_tot_profit_per = 0
            i = i + 2
            tot_qty = 0
            tot_cost = 0
            tot_inv_amount = 0
            tot_profit = 0
            tot_profit_per = 0
            sheet.write(i, 0, "Date", bold1)
            sheet.write(i, 1, "Invoice No.", bold)
            sheet.write(i, 2, "Barcode", bold1)
            sheet.write(i, 3, "Product", bold1)
            sheet.write(i, 4, "QTY", bold1)
            sheet.write(i, 5, "Cost", bold1)
            sheet.write(i, 6, "Sale Amount", bold1)
            sheet.write(i, 7, "Profit Amount", bold1)
            sheet.write(i, 8, "Profit %", bold1)
            i = i + 1
            for da in data:
                sheet.write(i, 0, str(da.get('invoice_date')), cell1)
                sheet.write(i, 1, da.get('invoice_number'), cell1)
                sheet.write(i, 2, da.get('barcode'), cell1)
                sheet.write(i, 3, da.get('product'), cell)
                sheet.write(i, 4, da.get('qty'), cell)
                tot_qty += int(da.get('qty'))
                g_tot_qty += int(da.get('qty'))
                sheet.write(i, 5, str(da.get('cost')) + ' ' + currency, cell)
                tot_cost += float(da.get('cost'))
                g_tot_cost += float(da.get('cost'))
                sheet.write(i, 6, str("%0.3f" % da.get('invoice_amount')) + ' ' + currency, cell)
                tot_inv_amount += float(da.get('invoice_amount'))
                g_tot_inv_amount += float(da.get('invoice_amount'))
                sheet.write(i, 7, str("%0.3f" % da.get('profit_amount')) + ' ' + currency, cell)
                tot_profit += float(da.get('profit_amount'))
                g_tot_profit += float(da.get('profit_amount'))
                sheet.write(i, 8, da.get('profit_per'), cell)
                tot_profit_per += float(da.get('profit_per'))
                g_tot_profit_per += float(da.get('profit_per'))
                i += 1
            sheet.write(i + 2, 0, 'Total:', bold)
            sheet.write(i + 2, 1, '----', bold)
            sheet.write(i + 2, 2, '----', bold)
            sheet.write(i + 2, 3, '----', bold)
            sheet.write(i + 2, 4, "%s" % g_tot_qty, bold1)
            sheet.write(i + 2, 5, "%0.3f" % g_tot_cost + ' ' + currency, bold1)
            sheet.write(i + 2, 6, "%0.3f" % g_tot_inv_amount + ' ' + currency, bold1)
            sheet.write(i + 2, 7, "%0.3f" % g_tot_profit + ' ' + currency, bold1)
            sheet.write(i + 2, 8, '----', bold)
            sheet.write(i + 2, 9, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.invoice.profit.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Invoice Profit Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
