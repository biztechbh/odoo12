
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


class WizardPurchaseOrderLineBarcode(models.TransientModel):
    _name = 'wizard.purchase.order.line.barcode'

    purchase_order_id = fields.Many2one('purchase.order', readonly=True, string = "Purchase Order")
    purchase_order_lines = fields.Many2many('purchase.order.line', string = "Purchase Order Lines")

    @api.model
    def default_get(self, field_list):
        res = super(WizardPurchaseOrderLineBarcode, self).default_get(field_list)
        purchase_order_lines = self.env['purchase.order.line'].search([('order_id', '=', self._context.get('active_id'))])
        res.update({
            'purchase_order_id' : self._context.get('active_id'),
            'purchase_order_lines': [(6, 0, purchase_order_lines.ids)],
        })
        return res

    def sent_for_print(self):
        product_label_qty = []
        for line in self.purchase_order_lines:
            lot_id = self.env['stock.production.lot'].search([('name', 'ilike', line.lot_number or False)], limit=1) or False
            data_vals = {
                'product_id': line.product_id.id,
                'stock_production_lot_id': lot_id.id if lot_id else False,
                'qty': line.product_qty + line.bonus_qty
            }
            product_label_qty.append((0, 0, data_vals))
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'wizard.product.small.label.report',
            'target': 'self',
            'context': {'default_product_ids': product_label_qty}
        }


