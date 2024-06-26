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

from odoo import fields, models, api, _
from datetime import datetime, date, timedelta


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    remaining_qty = fields.Float("Remaining Qty", compute="_compute_remaining_qty")
    expiry_state = fields.Selection([('expired', 'Expired'), ('near_expired', 'Near Expired')], string="Expiry State",
                                    compute="_get_product_state")
    state_check = fields.Selection([('expired', 'Expired'), ('near_expired', 'Near Expired')], string="state")
    sltech_barcode = fields.Char(related='product_id.barcode')

    @api.model
    def product_state_check(self):
        today_date = date.today()
        for each_stock_lot in self.env['stock.production.lot'].sudo().search([('life_date', '!=', False)]):
            if each_stock_lot.product_id.tracking != 'none':
                life_date = datetime.strptime(str(each_stock_lot.life_date), '%Y-%m-%d %H:%M:%S').date()
                if life_date < today_date:
                    each_stock_lot.write({'state_check': 'expired'})
                else:
                    if each_stock_lot.alert_date:
                        alert_date = datetime.strptime(str(each_stock_lot.alert_date), '%Y-%m-%d %H:%M:%S').date()
                        if alert_date <= today_date:
                            each_stock_lot.write({'state_check': 'near_expired'})
                        else:
                            each_stock_lot.write({'state_check': ''})
            else:
                each_stock_lot.write({'state_check': ''})

    def _compute_remaining_qty(self):
        for each in self:
            each.remaining_qty = 0
            for quant_id in each.quant_ids:
                if quant_id and quant_id.location_id and quant_id.location_id.usage == 'internal':
                    each.remaining_qty += quant_id.quantity
        return

    def get_lot_information(self, product_id, location_id):
        data = []
        quant_ids = self.env['stock.quant'].search([('product_id', '=', product_id), ('location_id', '=', location_id)])
        if quant_ids:
            for each in quant_ids:
                lot_info = self.search_read([('id', '=', each.lot_id.id)])
                for lot in lot_info:
                    lot['remaining_qty'] = each.quantity
                    data.append(lot)
        else:
            stock_inventory = self.env['stock.inventory'].search([('product_id', '=', product_id), ('location_id', '=', location_id)])
            for each in stock_inventory:
                lot_info = self.search_read([('id', '=', each.lot_id.id)])
                for each in lot_info:
                    data.append(each)
        return data

    @api.one
    @api.constrains('alert_date', 'life_date')
    def _check_dates(self):
        if self.alert_date and self.life_date:
            if not self.alert_date <= self.life_date:
                raise ValidationError(_('Dates must be: Alert Date < Expiry Date'))

    # 
    @api.model
    def name_search(self, name, args=None, operator='=', limit=100):
        if self._context.get('default_product_id'):
            stock_production_lot_obj = self.env['stock.production.lot']
            args = args or []
            recs = self.search([('product_id', operator, self._context.get('default_product_id'))])
            if recs:
                for each_stock_lot in recs:
                    if not each_stock_lot.life_date:
                        stock_production_lot_obj |= each_stock_lot
                    else:
                        if each_stock_lot.expiry_state != 'expired':
                            stock_production_lot_obj |= each_stock_lot
                return stock_production_lot_obj.name_get()
        return super(stock_production_lot, self).name_search(name, args, operator, limit)

    @api.one
    @api.depends('alert_date', 'life_date')
    def _get_product_state(self):
        today_date = date.today()
        for each_stock_lot in self.filtered(lambda l: l.life_date):
            if each_stock_lot.product_id.tracking != 'none':
                life_date = datetime.strptime(str(each_stock_lot.life_date), '%Y-%m-%d %H:%M:%S').date()
                if life_date < today_date:
                    each_stock_lot.expiry_state = 'expired'
                    each_stock_lot.write({'state_check': 'expired'})
                else:
                    if each_stock_lot.alert_date:
                        alert_date = datetime.strptime(str(each_stock_lot.alert_date), '%Y-%m-%d %H:%M:%S').date()
                        if alert_date <= today_date:
                            each_stock_lot.expiry_state = 'near_expired'
                            each_stock_lot.write({'state_check': 'near_expired'})
            else:
                each_stock_lot.write({'state_check': ''})

