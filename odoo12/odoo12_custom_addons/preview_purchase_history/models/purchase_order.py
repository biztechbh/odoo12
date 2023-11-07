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
    _inherit = 'purchase.order.line'

    @api.model
    def action_purchase_history(self, args):
        purchase_history = self.search([('product_id', '=', args), ('state', '=', 'purchase')], limit=10)
        view_id = self.env.ref('preview_purchase_history.purchase_history_wizard_view').id
        return purchase_history.ids, view_id

    def action_purchase_history_saved_line(self):
        purchase_history = self.search([('product_id', '=', self.product_id.id), ('state', '=', 'purchase')], limit=10)
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'name': 'Purchase History',
                'view_type': 'form',
                'res_model': 'purchase.history.wizard',
                'target': 'new',
                'context': {'default_preview_history': [(6, 0, purchase_history.ids)]},
                }
