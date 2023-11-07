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

    def get_daily_sales_data(self, from_dt, to_dt, categ_id, product_id, shop_id):
        tz_new = self.env.user.tz
        result_dict = {}
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d 00:00:00')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d 23:59:59')

        domain = f" (date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date between '{start_date}' AND '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        if shop_id:
            domain += " AND pos.shop_id = %s" % (shop_id)
        SQL = f'''
            select 
                pos.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}' as date_order,
                SUM(pol.price_unit) as rate, SUM(pol.price_subtotal) AS with_out_amount,
                SUM(pol.qty) as qty,SUM(ROUND(pol.price_subtotal_incl, 3)) as net_amount,
                SUM((pol.qty * pol.price_unit) * (pol.discount / 100)) AS discount, pos.name as invoice_number,
                pt.name as product_id, pp.barcode as barcode, poc.name as categ_name, uom.name as unit
                from pos_order_line as pol
                left join pos_order pos on pos.id = pol.order_id
                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join pos_category poc on poc.id = pt.pos_categ_id
                left join uom_uom uom on uom.id = pol.uom_id
            where{domain}
            group by pos.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', pt.name, 
                pp.barcode, poc.name, uom.name, pos.name
            order by to_char(pos.date_order at time zone 'UTC' at time zone '{tz_new}', 'YYYY-MM-DD')
        '''
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        return result

    def export_as_pdf_report_sales(self, from_dt, to_dt, categ_id, product_id, shop_id):

        data = self.get_daily_sales_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            d = from_dt + ' TO ' + to_dt
            rep_name = 'Daily sales report'
            summary = {
                'report_name': rep_name,
                'data': d
            }
            report_id = self.env['report.daily.sale.wizard.download'].create({
                'name': 'Daily sales report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'data_pdf': data,
                'summary': summary,
            })
            return report_id.id
        else:
            False

    def export_as_excel_report_sales(self, from_dt, to_dt, categ_id, product_id, shop_id):
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
        data = self.get_daily_sales_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            sheet.col(0).width = 256 * 15
            sheet.col(1).width = 256 * 15
            sheet.col(2).width = 256 * 15
            sheet.col(4).width = 256 * 10
            sheet.col(3).width = 256 * 50
            sheet.col(5).width = 256 * 10
            sheet.col(6).width = 256 * 15
            sheet.write_merge(0, 1, 0, 6, 'Daily sales report', heading)
            i = 3
            g_tot_qty = g_tot_rate = g_tot_with_out_amount = g_tot_discount = g_tot_net_amt = 0
            i = i + 2
            sheet.write(i, 0, "Date", bold1)
            sheet.write(i, 1, "Invoice No.", bold)
            sheet.write(i, 2, "Barcode", bold1)
            sheet.write(i, 3, "Product", bold1)
            sheet.write(i, 4, "Unit", bold1)
            sheet.write(i, 5, "QTY", bold1)
            sheet.write(i, 6, "Rate", bold1)
            sheet.write(i, 7, "Vat", bold1)
            sheet.write(i, 8, "Discount", bold1)
            sheet.write(i, 9, "Net Amount", bold1)
            i = i + 1
            for da in data:
                sheet.write(i, 0, str(da.get('date_order').date()), cell1)
                sheet.write(i, 1, da.get('invoice_number'), cell1)
                sheet.write(i, 2, da.get('barcode'), cell1)
                sheet.write(i, 3, da.get('product_id'), cell)
                sheet.write(i, 4, da.get('unit'), cell)
                sheet.write(i, 5, da.get('qty'), cell)
                g_tot_qty += float(da.get('qty'))
                sheet.write(i, 6, "%0.3f" % da.get('rate'), cell)
                g_tot_rate += float(da.get('rate'))
                sheet.write(i, 7, "%0.3f" % da.get('with_out_amount'), cell)
                g_tot_with_out_amount += float(da.get('with_out_amount'))
                sheet.write(i, 8, "%0.3f" % da.get('discount'), cell)
                g_tot_discount += float(da.get('discount'))
                sheet.write(i, 9, "%0.3f" % da.get('net_amount'), cell)
                g_tot_net_amt += float(da.get('net_amount'))
                i += 1
            sheet.write(i + 2, 0, '----', bold)
            sheet.write(i + 2, 1, '----', bold)
            sheet.write(i + 2, 2, '----', bold)
            sheet.write(i + 2, 3, '----', bold)
            sheet.write(i + 2, 4, '----', bold)
            sheet.write(i + 2, 5, "%d" % g_tot_qty, bold1)
            sheet.write(i + 2, 6, "%0.3f" % g_tot_rate, bold1)
            sheet.write(i + 2, 7, "%0.3f" % g_tot_with_out_amount, bold1)
            sheet.write(i + 2, 8, "%0.3f" % g_tot_discount, bold1)
            sheet.write(i + 2, 9, "%0.3f" % g_tot_net_amt, bold1)
            sheet.write(i + 2, 10, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.daily.sale.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Daily sales report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}
        else:
            False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
