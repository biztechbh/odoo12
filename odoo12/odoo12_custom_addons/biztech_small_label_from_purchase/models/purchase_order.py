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
