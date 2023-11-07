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
import xlwt, base64
from datetime import datetime
from dateutil.relativedelta import relativedelta as rd
from io import BytesIO


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_purchase_plan_data(self, from_dt, to_dt, categ_id, product_id):
        tz_new = self.env.user.tz
        start_date = datetime.strptime(from_dt, '%Y-%m-%d')
        end_date = datetime.strptime(to_dt, '%Y-%m-%d')
        count = 1
        while start_date < end_date:
            start_date += rd(months=1)
            count += 1
        previous_2_month = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d') - rd(months=2), '%Y-%m')
        previous_1_month = datetime.strftime(datetime.strptime(from_dt, '%Y-%m-%d') - rd(months=1), '%Y-%m')
        domain = " qty > 0 AND to_char(po.date_order, 'YYYY-MM') >= '%s' AND to_char(po.date_order, 'YYYY-MM') <= '%s'" % (previous_2_month, previous_1_month)
        if categ_id:
            domain += " AND poc.id = (%s)" % (categ_id)
        if product_id:
            domain += " AND pol.product_id = (%s)" % (product_id)
        SQL = f"""
                    SELECT 
                    pt.id, sum(pol.qty) as qty, pt.name as product, poc.name as categ_name
                    FROM pos_order_line pol
                    LEFT JOIN pos_order po on po.id = pol.order_id
                    left join product_product pp on pp.id = pol.product_id
                    left join product_template pt on pt.id = pp.product_tmpl_id
                    left join pos_category poc on poc.id = pt.pos_categ_id
                    WHERE {domain}
                    GROUP BY pt.id, pt.name, poc.name
                    ORDER BY pt.id
                    """
        self._cr.execute(SQL)
        result = self._cr.dictfetchall()
        main_dict = {}
        for each in result:
            if each.get('categ_name') is None:
                each['categ_name'] = 'Non-Defined'
            each['categ_name'] = str(each.get('categ_name')).replace(' ', '_')
            quant_id = self.env['stock.quant'].search([('product_id', '=', each.get('product_id'))])
            avg_qty = each.get('qty') / 2
            onhand_qty = sum([qty.quantity for qty in quant_id if qty.quantity > 0])
            plan_qty = avg_qty * count
            final_qty = plan_qty - onhand_qty if plan_qty > onhand_qty else 0
            each['final_qty'] = round(final_qty, 0)
            if each.get('categ_name') not in main_dict:
                main_dict[each.get('categ_name')] = [each]
            else:
                main_dict[each.get('categ_name')].append(each)
        return main_dict

    def export_as_pdf_report_purchase_plan(self,from_dt, to_dt, categ_id, product_id):

        data = self.get_purchase_plan_data(from_dt, to_dt, categ_id, product_id)

        d = from_dt + ' TO ' + to_dt

        rep_name = 'Purchase Planning report'
        summary = {
            'report_name': rep_name,
            'data': d
        }
        report_id = self.env['report.purchase.plan.wizard.download'].create({
            'name': 'Purchase Planning report - %s.pdf' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'data_pdf': data,
            'summary': summary,
        })
        return report_id.id

    def export_as_excel_report_purchase_plan(self, from_dt, to_dt, categ_id, product_id):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Report')
        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        heading = xlwt.easyxf('font: bold on, height 300; align: horiz center;')
        bold = xlwt.easyxf('font: bold on;')
        bold1 = xlwt.easyxf('font: bold on;align: horiz left;')
        cell1 = xlwt.easyxf('align: horiz left;')
        data = self.get_purchase_plan_data(from_dt, to_dt, categ_id, product_id)
        if data:
            sheet.col(0).width = 256 * 50
            sheet.col(1).width = 256 * 15
            sheet.col(2).width = 256 * 15
            sheet.write_merge(0, 1, 0, 6, 'Purchase Planning Report', heading)
            i = 3
            g_tot_qty = 0
            for d in data:
                sheet.write_merge(i + 1, i + 1, 0, 6,
                                  str(d).replace('_', ' ') or 'Non-Defined', bold)
                i = i + 2
                tot_qty = 0
                sheet.write(i, 0, "Product", bold1)
                sheet.write(i, 1, "QTY", bold1)
                i = i + 1
                for da in data[d]:
                    sheet.write(i, 0, da.get('product'), cell1)
                    sheet.write(i, 1, da.get('qty'), cell1)
                    tot_qty += float(da.get('qty'))
                    g_tot_qty += float(da.get('qty'))
                    i += 1
                sheet.write(i, 0, '', bold)
                sheet.write(i, 1, "%0.3f" % tot_qty, bold1)
                sheet.write(i, 2, '', bold1)
            sheet.write(i + 2, 0, 'Total', bold)
            sheet.write(i + 2, 1, "%0.3f" % g_tot_qty, bold1)
            sheet.write(i + 2, 2, '', bold)
            file_data = BytesIO()
            workbook.save(file_data)
            report_id = self.env['report.purchase.plan.wizard.download'].create({
                'data': base64.encodestring(file_data.getvalue()),
                'name': 'Purchase Planning Report - %s.xls' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            })
            return {'report_id': report_id.id}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: