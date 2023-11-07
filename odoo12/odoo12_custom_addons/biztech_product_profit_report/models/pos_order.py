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

from odoo import models, fields, api, _
import calendar, xlwt, base64
from datetime import datetime, timedelta
from io import BytesIO


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_product_profit_data(self, from_dt, to_dt, categ_id, product_id, shop_id):
        tz_new = self.env.user.tz
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d 00:00:00')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d 23:59:59')
        print("\n\n\n>>>shop_id>>>>",shop_id)
        domain = f" (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date >= '{start_date}' AND (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        if shop_id:
            domain += " AND po.shop_id = (%s)" % (shop_id)
        SQL = f'''
            select 
                TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'YYYY') as year,
                TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'MM') as month,
                TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'Mon-YYYY') as month_year,
                po.id, count(po.id) as count, pt.name as prod_name, pp.barcode, pp.id as prod_id,
                poc.name as categ_name, SUM(pol.qty) as qty, SUM(pol.price_subtotal) as total_sale, pol.cost_price as cost_price
                from pos_order_line as pol
                left join pos_order po on pol.order_id = po.id
                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join pos_category poc on poc.id = pt.pos_categ_id
                where {domain}
                group by po.id, pt.name, pp.id, poc.name, pol.cost_price
                order by year, month
        '''
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        main_dict = {}
        for each in result:
#             cost_price = self.env['product.product'].browse(each.get('prod_id')).standard_price
            cost_price = each.get('cost_price')
            cost = float("%0.3f" % cost_price) * each.get('qty')
            total_sale = each.get('total_sale')
            profit = total_sale - cost
            profit_pr = (((total_sale - cost) * 100) / cost) if cost != 0 else 100
            each['total_sale'] = float("%0.3f" % total_sale)
            each['cost'] = float("%0.3f" % cost)
            each['profit'] = float("%0.3f" % profit)
            each['profit_per'] = float("%0.3f" % profit_pr)
            if each.get('month_year') not in main_dict:
                main_dict[each.get('month_year')] = [each]
            else:
                main_dict[each.get('month_year')].append(each)
        return result

    def export_as_pdf_report_product_profit(self, from_dt, to_dt, categ_id, product_id, shop_id):
        data = self.get_product_profit_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            d = from_dt + ' TO ' + to_dt
            rep_name = 'Product Sales Profit Report'
            summary = {
                'report_name': rep_name,
                'data': d
            }
            report_id = self.env['report.product.profit.wizard.download'].create({
                'name': 'Product Sales Profit Report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'data_pdf': data,
                'summary': summary,
            })
            return report_id.id
        else:
            False

    def export_as_excel_report_product_profit(self, from_dt, to_dt, categ_id, product_id, shop_id):
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
        data = self.get_product_profit_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            sheet.col(0).width = 256 * 15
            sheet.col(1).width = 256 * 20
            sheet.col(2).width = 256 * 20
            sheet.col(4).width = 256 * 20
            sheet.col(5).width = 256 * 20
            sheet.col(3).width = 256 * 20
            sheet.col(6).width = 256 * 20
            sheet.col(7).width = 256 * 20
            sheet.col(8).width = 256 * 20
            sheet.write_merge(0, 1, 0, 6, 'Product Sales Profit Report', heading)
            i = 3
            g_tot_count = g_tot_cost = g_tot_sale = g_tot_profit = g_tot_profit_per = 0
            i = i + 2
            sheet.write(i, 0, "Month-Year", bold)
            sheet.write(i, 1, "No. of Patients", bold1)
            sheet.write(i, 2, "Barcode", bold1)
            sheet.write(i, 3, "Product", bold1)
            sheet.write(i, 4, "Quantity", bold1)
            sheet.write(i, 5, "Total Sale", bold1)
            sheet.write(i, 6, "Cost of Sale", bold1)
            sheet.write(i, 7, "Profit Amount", bold1)
            sheet.write(i, 8, "Profit %", bold1)
            i = i + 1
            for d in data:
                sheet.write(i, 0, str(d.get('month_year')), cell1)
                sheet.write(i, 1, d.get('count'), cell)
                g_tot_count += float(d.get('count'))
                sheet.write(i, 2, d.get('barcode'), cell)
                sheet.write(i, 3, d.get('prod_name'), cell)
                sheet.write(i, 4, d.get('qty'), cell)
                sheet.write(i, 5, "%0.3f" % d.get('total_sale') + ' ' + currency, cell)
                g_tot_sale += float(d.get('total_sale'))
                sheet.write(i, 6, str("%0.3f" % d.get('cost')) + ' ' + currency, cell)
                g_tot_cost += float(d.get('cost'))
                sheet.write(i, 7, str("%0.3f" % d.get('profit')) + ' ' + currency, cell)
                g_tot_profit += float(d.get('profit'))
                sheet.write(i, 8, "%0.2f" % d.get('profit_per'), cell)
                g_tot_profit_per += float(d.get('profit_per'))
                i += 1
            sheet.write(i + 2, 0, 'Total:', bold)
            sheet.write(i + 2, 1, "%d" % g_tot_count, bold1)
            sheet.write(i + 2, 2, '------', bold)
            sheet.write(i + 2, 3, '------', bold)
            sheet.write(i + 2, 4, '------', bold)
            sheet.write(i + 2, 5, "%0.3f" % g_tot_sale + ' ' + currency, bold1)
            sheet.write(i + 2, 6, "%0.3f" % g_tot_cost + ' ' + currency, bold1)
            sheet.write(i + 2, 7, "%0.3f" % g_tot_profit + ' ' + currency, bold1)
            sheet.write(i + 2, 8, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.product.profit.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Product Sales Profit Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}
        else:
            False
            
class pos_order_line(models.Model):
    _inherit = 'pos.order.line'
    
    cost_price_updated = fields.Boolean(string="Cost Price Updated")
    profit_amount = fields.Float(string="Profit Amt", compute='compute_product_profit_amount', store=True)
    profit_percentage = fields.Float(string="Profit %", compute='compute_product_profit_amount', store=True)
#     cost_subtotal = fields.Float(string="Cost Subtotal", compute='compute_cost_subtotal', store=True)
    
    @api.depends('price_subtotal_incl','cost_price','qty')
    def compute_product_profit_amount(self):
        for pos_line in self:
            cost = pos_line.cost_price * pos_line.qty
            total_sale = pos_line.price_subtotal
            profit_amt = total_sale - cost
            profit_percent = (((total_sale - cost) * 100) / cost) if cost != 0 else 100
            pos_line.update({
                'profit_amount': profit_amt,
                'profit_percentage': profit_percent,
                })
            

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
