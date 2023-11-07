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

month_str = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_monthly_sales_data(self, from_dt, to_dt, categ_id, product_id, shop_id):
        tz_new = self.env.user.tz
        result_dict = {}
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d')

        domain = f" (pos.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date >= '{start_date}' AND (pos.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        if shop_id:
            domain += " AND pos.shop_id = (%s)" % (shop_id)
        SQL = f'''
            select uom.name as unit,
                pos.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}' as date_order,
                SUM(pol.qty) as qty,
                SUM(pol.price_unit) as rate,
                poc.name as categ_name,  
                pt.name as product_id,
                SUM((pol.qty * pol.price_unit) * (pol.discount / 100)) AS discount,
                SUM(ROUND(pol.price_subtotal_incl, 3)) as net_amount,
                SUM(ROUND(pol.price_subtotal, 3)) as with_out_amount, 
                pp.barcode as barcode
                from pos_order_line as pol
                left join pos_order pos on pos.id = pol.order_id
                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join pos_category poc on poc.id = pt.pos_categ_id
                left join uom_uom uom on uom.id = pol.uom_id 
            where{domain}
            group by poc.id, uom.name, pos.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}',
            pos.id, pt.name, pp.barcode
            order by pos.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}'
        '''
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        for each in result:
            if each.get('net_amount') and each.get('with_out_amount'):
                each['with_out_amount'] = round(float(each['net_amount']) - float(each['with_out_amount']), 3)
            start_dates = self.get_date_ranges_monthwise(datetime.strptime(from_dt, '%Y-%m-%d'),
                                                         datetime.strptime(to_dt, '%Y-%m-%d'))
            month_range = [each.get('date_order').month, each.get('date_order').year]
            if month_range in start_dates:
                month_range_str = month_str.get(month_range[0]) + "-" + str(month_range[1])
                each.update({"card_title": month_range_str})
                if not result_dict.get(month_range_str, False):
                    result_dict.update({month_range_str: [each]})
                else:
                    result_dict[month_range_str] += [each]
        return result_dict

    def get_date_ranges_monthwise(self, start_date, end_date):
        start_dates = [[start_date.month, start_date.year]]
        end_dates = []
        begin_date = start_date
        one_day = timedelta(1)

        while begin_date <= end_date:
            next_day = begin_date + one_day
            if next_day.month != begin_date.month:
                start_dates.append([next_day.month, next_day.year])
            begin_date = next_day
        return start_dates

    def export_as_pdf_monthly_report_sales(self, from_dt, to_dt, categ_id, product_id, shop_id):

        data = self.get_monthly_sales_data(from_dt, to_dt, categ_id, product_id, shop_id)

        d = from_dt + ' TO ' + to_dt

        rep_name = 'Monthly sales report' or 'Non-Defined'
        summary = {
            'report_name': rep_name,
            'data': d
        }
        report_id = self.env['report.monthly.wizard.download'].create({
            'name': 'Monthly sales report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'data_pdf': data,
            'summary': summary,
        })
        return report_id.id

    def export_as_excel_monthly_report_sales(self, from_dt, to_dt, categ_id, product_id, shop_id):
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
        data = self.get_monthly_sales_data(from_dt, to_dt, categ_id, product_id, shop_id)
        data = sorted(data.items())
        if data:
            sheet.col(0).width = 256 * 15
            sheet.col(1).width = 256 * 50
            sheet.col(2).width = 256 * 20
            sheet.col(3).width = 256 * 20

            sheet.write_merge(0, 1, 0, 6, 'Monthly Sales Report', heading)
            i = 3
            g_tot_qty = g_tot_rate = g_tot_with_out_amount = g_tot_discount = g_tot_net_amt = 0
            for d in data:
                sheet.write_merge(i + 1, i + 1, 0, 6,
                                  d[1][0].get('card_title') or 'Non-Defined', bold)
                i = i + 2
                tot_amt = 0
                tot_qty = 0
                tot_rate = 0
                tot_with_out_amount = 0
                tot_discount = 0
                tot_net_amt = 0
                sheet.write(i, 0, "Barcode", bold1)
                sheet.write(i, 1, "Product", bold1)
                sheet.write(i, 2, "Unit", bold1)
                sheet.write(i, 3, "QTY", bold1)
                sheet.write(i, 4, "Vat", bold1)
                sheet.write(i, 5, "Net Amount", bold1)
                i = i + 1
                for da in d[1]:
                    sheet.write(i, 0, da.get('barcode'), cell1)
                    sheet.write(i, 1, da.get('product_id'), cell)
                    sheet.write(i, 2, da.get('unit'), cell)
                    sheet.write(i, 3, da.get('qty'), cell)
                    tot_qty += float(da.get('qty'))
                    g_tot_qty += float(da.get('qty'))
                    tot_rate += float(da.get('rate'))
                    g_tot_rate += float(da.get('rate'))
                    sheet.write(i, 4, "%0.3f" % da.get('with_out_amount'), cell)
                    tot_with_out_amount += float(da.get('with_out_amount'))
                    g_tot_with_out_amount += float(da.get('with_out_amount'))
                    tot_discount += float(da.get('discount'))
                    g_tot_discount += float(da.get('discount'))
                    sheet.write(i, 5, "%0.3f" % da.get('net_amount'), cell)
                    tot_net_amt += float(da.get('net_amount'))
                    g_tot_net_amt += float(da.get('net_amount'))
                    i += 1
                sheet.write(i, 0, '', bold)
                sheet.write(i, 1, '', bold)
                sheet.write(i, 2, '', bold)
                sheet.write(i, 3, "%0.3f" % tot_qty, bold1)
                sheet.write(i, 4, "%0.3f" % tot_with_out_amount, bold1)
                sheet.write(i, 5, "%0.3f" % tot_net_amt, bold1)
                sheet.write(i, 6, '', bold1)
            sheet.write(i + 2, 0, '----', bold)
            sheet.write(i + 2, 1, '----', bold)
            sheet.write(i + 2, 2, '----', bold)
            sheet.write(i + 2, 3, "%0.3f" % g_tot_qty, bold1)
            sheet.write(i + 2, 4, "%0.3f" % g_tot_with_out_amount, bold1)
            sheet.write(i + 2, 5, "%0.3f" % g_tot_net_amt, bold1)
            sheet.write(i + 2, 6, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.monthly.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Monthly Sales Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
