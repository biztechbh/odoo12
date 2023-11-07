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
from odoo.exceptions import Warning
import calendar, xlwt, base64
from datetime import datetime, timedelta
from collections import OrderedDict
from babel.numbers import format_decimal
from io import BytesIO


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_sales_profit_data(self, from_dt, to_dt, categ_id, product_id, shop_id):
        tz_new = self.env.user.tz
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d')

        domain = f" (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Bahrain')::date >= '{start_date}' AND (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Bahrain')::date <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        if shop_id:
            domain += " AND po.shop_id = (%s)" % (shop_id)
        SQL = f'''
            select 
            TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'YYYY-MM-DD') as date_order,
            COALESCE(sum(round(pol.cost_price, 3)),0.0) as cost,
            poc.name as categ_name,
            round(sum(pol.price_subtotal_incl - pol.cost_price)::numeric, 3) as profit_amount,
            pp.id as prod_id,
            SUM(pol.price_subtotal_incl) as invoice_amount
            from pos_order_line as pol
            left join pos_order po on po.id = pol.order_id
            left join product_product pp on pp.id = pol.product_id
            left join product_template pt on pt.id = pp.product_tmpl_id
            left join pos_category poc on poc.id = pt.pos_categ_id
            where{domain}
            group by TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'YYYY-MM-DD'), poc.name, pp.id
            order by TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'YYYY-MM-DD')
        '''
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        for each in result:
            try:
                each['profit_per'] = round(each['profit_amount'] * 100 / each['cost'], 3)
            except:
                each['profit_per'] = round(100, 3)
        main_dict = {}
        for each1 in result:
            if each1.get('date_order') in main_dict:
                cost = round(each1['cost'] + main_dict[each1.get('date_order')]['cost'], 3)
                profit_amount = round(each1['profit_amount'] + main_dict[each1.get('date_order')]['profit_amount'], 3)
                profit_per = round((profit_amount * 100) / cost, 3)
                main_dict[each1.get('date_order')].update({
                    'invoice_amount': round(each1['invoice_amount'] + main_dict[each1.get('date_order')]['invoice_amount'], 3),
                    'cost': cost,
                    'profit_amount': profit_amount,
                    'profit_per': profit_per,
                })
                test = main_dict[each1.get('date_order')]
                main_dict[each1.get('date_order')] = test
            else:
                main_dict[each1.get('date_order')] = each1
        return main_dict

    def export_as_pdf_report_sales_profit(self, from_dt, to_dt, categ_id, product_id, shop_id):
        data = self.get_sales_profit_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            d = from_dt + ' TO ' + to_dt

            rep_name = 'Sales Profit Report'
            summary = {
                'report_name': rep_name,
                'data': d
            }
            report_id = self.env['report.sale.profit.wizard.download'].create({
                'name': 'Sales profit report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'data_pdf': data,
                'summary': summary,
            })
            return report_id.id
        else:
            return False

    def export_as_excel_report_sales_profit(self, from_dt, to_dt, categ_id, product_id, shop_id):
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
        data = self.get_sales_profit_data(from_dt, to_dt, categ_id, product_id, shop_id)
        data = data.values()
        if data:
            sheet.col(0).width = 256 * 20
            sheet.col(1).width = 256 * 20
            sheet.col(2).width = 256 * 20
            sheet.col(4).width = 256 * 20
            sheet.col(3).width = 256 * 20
            sheet.write_merge(0, 1, 0, 6, 'Sales Profit Report', heading)
            i = 3
            g_tot_inv_amt = g_tot_cost = g_tot_profit = g_tot_profit_per = 0
            i = i + 2
            # tot_inv_amt = 0
            # tot_cost = 0
            # tot_profit = 0
            # tot_profit_per = 0
            sheet.write(i, 0, "Date", bold1)
            sheet.write(i, 1, "Invoice Amount", bold)
            sheet.write(i, 2, "Cost of Sale", bold1)
            sheet.write(i, 3, "Profit", bold1)
            sheet.write(i, 4, "Profit %", bold1)
            i = i + 1
            for da in data:
                sheet.write(i, 0, str(da.get('date_order')), cell1)
                sheet.write(i, 1, str("%0.3f" % da.get('invoice_amount')) + ' ' + currency, cell)
                # tot_inv_amt += float(da.get('invoice_amount'))
                g_tot_inv_amt += float(da.get('invoice_amount'))
                sheet.write(i, 2, str("%0.3f" % da.get('cost')) + ' ' + currency, cell)
                # tot_cost += float(da.get('cost'))
                g_tot_cost += float(da.get('cost'))
                sheet.write(i, 3, str("%0.3f" % da.get('profit_amount')) + ' ' + currency, cell)
                # tot_profit += float(da.get('profit_amount'))
                g_tot_profit += float(da.get('profit_amount'))
                sheet.write(i, 4, str("%0.3f" % da.get('profit_per')) + ' %', cell)
                i += 1

            sheet.write(i + 2, 0, 'Total:', bold)
            sheet.write(i + 2, 1, "%0.3f" % g_tot_inv_amt + ' ' + currency, bold1)
            sheet.write(i + 2, 2, "%0.3f" % g_tot_cost + ' ' + currency, bold1)
            sheet.write(i + 2, 3, "%0.3f" % g_tot_profit + ' ' + currency, bold1)
            sheet.write(i + 2, 4, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.sale.profit.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Sales profit report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}
        else:
            return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
