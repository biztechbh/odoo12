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
from odoo.exceptions import Warning, ValidationError
from datetime import datetime, date


class WizardSaleVATDashboardReport(models.TransientModel):
    _name = 'wizard.sale.vat.dashboard.report'

    from_date = fields.Date(string="From", required=True, default=date.today())
    to_date = fields.Date(string="To", required=True, default=date.today())
    categ_id = fields.Many2one('pos.category', string='Category')
    product_id = fields.Many2one('product.product', string="Product")
    shop_id = fields.Many2one('pos.shop', string="Branch")

    @api.multi
    def action_dashboard(self):
        action_context = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'categ_id': self.categ_id.id,
            'product_id': self.product_id.id,
            'shop_id': self.shop_id.id,
        }
        return {
            'name': 'Sale VAT Report',
            'type': 'ir.actions.client',
            'tag': 'open_sale_vat_report_view',
            'context': action_context,
            'target': 'main'
        }

    @api.onchange('categ_id')
    def onchange_pos_category(self):
        if not self.categ_id:
            return {'domain': {'product_id': []}}
        return {'domain': {'product_id': [
            ('pos_categ_id', '=', self.categ_id.id),
        ]}}

    @api.onchange('product_id')
    def onchange_product(self):
        if not self.product_id:
            return {'domain': {'categ_id': []}}
        return {'domain': {'categ_id': [
            ('id', '=', self.product_id.pos_categ_id.id),
        ]}}

    @api.constrains('from_date', 'to_date')
    def check_date_range(self):
        if self.to_date and self.from_date:
            if datetime.strptime(str(self.to_date), "%Y-%m-%d") < datetime.strptime(str(self.from_date), "%Y-%m-%d"):
                raise ValidationError(_("End Date should be greater than Start Date."))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

