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

from odoo import api, fields, models, _

class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'

    def sent_for_print(self):
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'name': 'Print Barcode',
                'view_type': 'form',
                'res_model': 'wizard.purchase.order.line.barcode',
                'target': 'new',
                # 'context': {'default_purchase_order_id': },
                }


class ProductInherit(models.Model):
    _inherit = 'product.product'

    def sent_for_print(self):
        product_label_qty = []
        for line in self:

            data_vals = {
                'product_id': line.id,
                'qty': 1
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


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    def sent_for_print(self):
        product_label_qty = []
        for line in self:
            data_vals = {
                'product_id': line.id,
                'qty': 1
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