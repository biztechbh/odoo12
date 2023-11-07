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
from io import BytesIO


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_monthly_time_based_data(self, from_dt, to_dt, categ_id, product_id, shop_id):
        tz_new = self.env.user.tz
        start_date = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d'), '%Y-%m-%d 00:00:00')
        end_date = datetime.strftime(datetime.strptime(to_dt, '%Y-%m-%d'), '%Y-%m-%d 23:59:59')

        domain = f"(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date >= '{start_date}' AND (po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}')::date <= '{end_date}'"
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        if shop_id:
            domain += " AND po.shop_id = (%s)" % (shop_id)
        SQL = f'''
            select 
                po.id as order_id, TO_CHAR(po.date_order AT TIME ZONE 'UTC' AT TIME ZONE '{tz_new}', 'Mon-YYYY') as month_year,
                round(sum(pol.price_subtotal_incl), 3) as total_sale, round(sum(pol.cost_price::numeric), 3) as cost, 
                round(sum(pol.price_subtotal_incl - pol.cost_price)::numeric, 3) as profit, 
                poc.name as categ_name
                from pos_order_line as pol
                left join pos_order as po on po.id = pol.order_id
                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join pos_category poc on poc.id = pt.pos_categ_id
                where {domain}
                group by month_year, po.id, poc.name
                order by month_year, po.id
        '''
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        result_dict = {}
        main_dict = {}
        for each1 in result:
            try:
                each1['profit_per'] = each1['profit'] * 100 / each1['cost']
            except:
                each1['profit_per'] = 100

            each1['total_sale'] = round(each1.get('total_sale'), 3)
            each1['cost'] = round(each1.get('cost') or 0.00, 3)
            each1['profit'] = round(each1.get('profit') or 0.00, 3)
            each1['profit_per'] = round(each1.get('profit_per') or 0.00, 3)

            # if each.get('categ_name') is None:
            #     each['categ_name'] = 'Non-Defined'
            # each['categ_name'] = str(each.get('categ_name')).replace(' ', '_')
            # if each.get('categ_name') not in main_dict:
            #     main_dict[each.get('categ_name')] = [each]
            # else:
            #     main_dict[each.get('categ_name')].append(each)
        temp_list = []
        # for rec in result:
        #     temp_dict = {}
        #     for each1 in rec:
        #         if each1.get('categ_name') not in temp_dict:
        #             temp_dict[each1.get('categ_name')] = {
        #                 'month_year': each1.get('month_year'),
        #                 'categ_name': each1.get('categ_name'),
        #                 'count': 1,
        #                 'total_sale': round(each1.get('total_sale'), 3),
        #                 'cost': round(each1.get('cost'), 3),
        #                 'profit': round(each1.get('profit'), 3),
        #                 'profit_per': round(each1.get('profit_per'), 3)
        #             }
        #         else:
        #             temp_dict[each1.get('categ_name')].update({
        #                 'month_year': each1.get('month_year'),
        #                 'categ_name': each1.get('categ_name'),
        #                 'count': temp_dict[each1.get('categ_name')].get('count') + 1,
        #                 'total_sale': round((each1.get('total_sale') + temp_dict[each1.get('categ_name')].get('total_sale')), 3),
        #                 'cost': round((each1.get('cost') or 0.00 + temp_dict[each1.get('categ_name')].get('cost')), 3),
        #                 'profit': round((each1.get('profit') or 0.00 + temp_dict[each1.get('categ_name')].get('profit')), 3),
        #                 'profit_per': round((each1.get('profit_per') or 0.00 + temp_dict[each1.get('categ_name')].get('profit_per')), 3),
        #             })
        #     temp_list.append(temp_dict)
        # for record in temp_list:
        #     for i in record.values():
        #         if i.get('categ_name') not in result_dict:
        #             result_dict[i.get('categ_name')] = [i]
        #         else:
        #             result_dict[i.get('categ_name')].append(i)
        return result

    def export_as_pdf_report_monthly_time_based(self, from_dt, to_dt, categ_id, product_id, shop_id):

        data = self.get_monthly_time_based_data(from_dt, to_dt, categ_id, product_id, shop_id)
        if data:
            d = from_dt + ' TO ' + to_dt
            rep_name = 'Monthly Time Based Report'
            summary = {
                'report_name': rep_name,
                'data': d
            }
            report_id = self.env['report.monthly.time.based.wizard.download'].create({
                'name': 'Monthly Time Based Report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'data_pdf': data,
                'summary': summary,
            })
            return report_id.id
        else:
            False

    def export_as_excel_report_monthly_time_based(self, from_dt, to_dt, categ_id, product_id, shop_id):
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
        data = self.get_monthly_time_based_data(from_dt, to_dt, categ_id, product_id, shop_id)
        data = sorted(data.items())
        if data:
            sheet.col(0).width = 256 * 15
            sheet.col(1).width = 256 * 20
            sheet.col(2).width = 256 * 20
            sheet.col(4).width = 256 * 20
            sheet.col(3).width = 256 * 20
            sheet.col(5).width = 256 * 20
            sheet.col(6).width = 256 * 20
            sheet.col(7).width = 256 * 20
            sheet.write_merge(0, 1, 0, 6, 'Monthly Time Based Report', heading)
            i = 3
            g_tot_count = g_tot_cost = g_tot_sale = g_tot_profit = g_tot_profit_per = 0
            for d in data:
                sheet.write_merge(i + 1, i + 1, 0, 6,
                                  str(d[1][0].get('categ_name')).replace('_', ' '), bold)
                i = i + 2
                tot_count = 0
                tot_cost = 0
                tot_sale = 0
                tot_profit = 0
                tot_profit_per = 0
                sheet.write(i, 0, "Month-Year", bold)
                sheet.write(i, 1, "No. of Patients", bold1)
                sheet.write(i, 2, "Total Sale", bold1)
                sheet.write(i, 3, "Cost of Sale", bold1)
                sheet.write(i, 4, "Profit Amount", bold1)
                sheet.write(i, 5, "Profit %", bold1)
                i = i + 1
                for da in d[1]:
                    sheet.write(i, 0, str(da.get('month_year')), cell1)
                    sheet.write(i, 1, da.get('count'), cell)
                    tot_count += float(da.get('count'))
                    g_tot_count += float(da.get('count'))
                    sheet.write(i, 2, "%0.3f" % da.get('total_sale') + ' ' + currency, cell)
                    tot_sale += float(da.get('total_sale'))
                    g_tot_sale += float(da.get('total_sale'))
                    sheet.write(i, 3, str("%0.3f" % da.get('cost')) + ' ' + currency, cell)
                    tot_cost += float(da.get('cost'))
                    g_tot_cost += float(da.get('cost'))
                    sheet.write(i, 4, str("%0.3f" % da.get('profit')) + ' ' + currency, cell)
                    tot_profit += float(da.get('profit'))
                    g_tot_profit += float(da.get('profit'))
                    sheet.write(i, 5, "%0.3f" % da.get('profit_per'), cell)
                    # tot_profit_per += float(da.get('profit_per'))
                    # g_tot_profit_per += float(da.get('profit_per'))
                    i += 1
                sheet.write(i, 0, '------', bold)
                sheet.write(i, 1, "%0.3f" % tot_count, bold1)
                sheet.write(i, 2, "%0.3f" % tot_sale, bold1)
                sheet.write(i, 3, "%0.3f" % tot_cost + ' ' + currency, bold1)
                sheet.write(i, 4, "%0.3f" % tot_profit + ' ' + currency, bold1)
                sheet.write(i, 5, '', bold1)
            sheet.write(i + 2, 0, 'Total:', bold)
            sheet.write(i + 2, 1, "%0.3f" % g_tot_count, bold1)
            sheet.write(i + 2, 2, "%0.3f" % g_tot_sale, bold1)
            sheet.write(i + 2, 3, "%0.3f" % g_tot_cost + ' ' + currency, bold1)
            sheet.write(i + 2, 4, "%0.3f" % g_tot_profit + ' ' + currency, bold1)
            sheet.write(i + 2, 5, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.monthly.time.based.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Monthly Time Based Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
