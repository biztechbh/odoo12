# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2020-Today(www.slecherpsolution.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import xlwt
import base64
from io import BytesIO
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlwt
from odoo.exceptions import Warning
from odoo import models, fields, api, _

class ProductExpiryReport(models.Model):
    _inherit = "product.expiry.report"

    @api.multi
    def print_product_expiry_report(self, report_type):
        if self.num_expiry_days <= 0:
            raise Warning(_('Number Of Expiry Days should be greater then 0'))
        location_ids = self.location_ids.ids or self.env['stock.location'].search([('usage', '=', 'internal')]).ids
        category_ids = self.category_ids.ids or self.env['product.category'].search([]).ids
        SQL1 = '''SELECT sq.location_id,sl.usage,spl.product_id,spl.id,spl.life_date,spl.name,pc.name as product_category,
                                pp.default_code,pt.name as product_name 
                        FROM stock_production_lot spl
                                LEFT JOIN stock_quant sq on sq.lot_id = spl.id
                                LEFT JOIN stock_location sl on sq.location_id = sl.id
                                LEFT JOIN product_product pp on spl.product_id = pp.id
                                LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
                                LEFT JOIN product_category pc on pt.categ_id = pc.id
                        WHERE spl.life_date AT TIME ZONE 'GMT' <= '%s' AND
                                    spl.life_date AT TIME ZONE 'GMT' >= '%s' AND
                                    pc.id IN %s order by pp.default_code''' % (
            (date.today() + timedelta(days=self.num_expiry_days)),
            date.today(),
            "(%s)" % ','.join(map(str, category_ids)))
        self.env.cr.execute(SQL1)
        res1 = self.env.cr.dictfetchall()

        temp_res = []
        for each in res1:
            if each.get('usage') in ['internal',None]:
                temp_res.append(each)
        SQL = '''SELECT sq.location_id,sl.usage,spl.product_id,spl.id,spl.life_date,spl.name,pc.name as product_category,
                                        pp.default_code,pt.name as product_name FROM stock_quant sq
                                        LEFT JOIN stock_location sl on sq.location_id = sl.id
                                        LEFT JOIN stock_production_lot spl on sq.lot_id = spl.id
                                        LEFT JOIN product_product pp on spl.product_id = pp.id
                                        LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
                                        LEFT JOIN product_category pc on pt.categ_id = pc.id
                                        WHERE spl.life_date AT TIME ZONE 'GMT' <= '%s' AND
                                        spl.life_date AT TIME ZONE 'GMT' >= '%s' AND
                                        pc.id IN %s AND
                                        sq.location_id IN %s order by pp.default_code''' % (
            (date.today() + timedelta(days=self.num_expiry_days)),
            date.today(),
            "(%s)" % ','.join(map(str, category_ids)),
            "(%s)" % ','.join(map(str, location_ids)))
        self.env.cr.execute(SQL)
        res = self.env.cr.dictfetchall()
        if not self.location_ids:
            res = res + temp_res
            res = [dict(t) for t in {tuple(d.items()) for d in res}]
        if len(res) == 0:
            raise Warning(_('No such record found for product expiry.'))
        else:
            if self.group_by == 'category':
                vals = {}
                for each in res:
                    if each.get('location_id') == None:
                        location_name = "--"
                    else:
                        location_name = self.env['stock.location'].browse(
                            each.get('location_id')).display_name
                    if each['product_category'] not in vals:
                        vals[each.get('product_category')] = [
                            {'name': each.get('name'),
                             'product_id': each.get('product_name'),
                             'location_name': location_name,
                             'default_code': each.get('default_code') or '--------',
                             'life_date': each.get('life_date').strftime('%Y-%m-%d'),
                             'remaining_days': (each.get('life_date').date() - date.today()).days,
                             'available_qty': self.env['stock.production.lot'].browse(each.get('id')).product_qty if each.get('id') else False,}]
                    else:
                        vals[each.get('product_category')].append(
                            {'name': each.get('name'),
                             'product_id': each.get('product_name'),
                             'location_name': location_name,
                             'default_code': each.get('default_code') or '--------',
                             'life_date': each.get('life_date').strftime('%Y-%m-%d'),
                             'remaining_days': (each.get('life_date').date() - date.today()).days,
                             'available_qty': self.env['stock.production.lot'].browse(each.get('id')).product_qty if each.get('id') else False,})
            else:
                vals = {}
                for each in res:
                    if each.get('location_id') == None:
                        location_name = "--"
                    else:
                        location_name = self.env['stock.location'].browse(
                            each.get('location_id')).display_name
                    if location_name not in vals:
                        vals[location_name] = [
                            {'name': each.get('name'),
                             'product_id': each.get('product_name'),
                             'product_category': each.get('product_category'),
                             'default_code': each.get('default_code') or '--------',
                             'life_date': each.get('life_date').strftime('%Y-%m-%d'),
                             'remaining_days': (each.get('life_date').date() - date.today()).days,
                             'available_qty': self.env['stock.production.lot'].browse(each.get('id')).product_qty if each.get('id') else False,}]
                    else:
                        vals[location_name].append(
                            {'name': each.get('name'),
                             'product_id': each.get('product_name'),
                             'product_category': each.get('product_category'),
                             'default_code': each.get('default_code') or '--------',
                             'life_date': each.get('life_date').strftime('%Y-%m-%d'),
                             'remaining_days': (each.get('life_date').date() - date.today()).days,
                             'available_qty': self.env['stock.production.lot'].browse(each.get('id')).product_qty if each.get('id') else False,})
        vals.update(
            {'group_by': self.group_by, 'num_days': self.num_expiry_days, 'today_date': date.today()})
        vals_new = {}
        vals_new.update({'stock': vals})
        if report_type == 'pdf':
            return self.env.ref('flexipharmacy.product_expiry_report').report_action(self,
                                                                                     data=vals_new)
        elif report_type == 'xls':
            return self.print_xls_product_report(vals)
