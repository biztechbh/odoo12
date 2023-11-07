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
from odoo.exceptions import Warning
from datetime import datetime


class WizardSalesDashboardReport(models.TransientModel):
    _name = 'wizard.monthly.sales.dashboard.report'
    _description = 'POS Monthly Sales Dashboard Wizard'

    from_date = fields.Date(string="From", required=True)
    to_date = fields.Date(string="To", required=True)
    categ_id = fields.Many2one('pos.category', string='Category')
    product_id = fields.Many2one('product.product', string="Product")
    shop_id = fields.Many2one('pos.shop', string="Branch")

    @api.multi
    def action_dashboard(self):
        action_context = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'categ_id': self.categ_id.id if self.categ_id else False,
            'product_id': self.product_id.id if self.product_id else False,
            'shop_id': self.shop_id.id if self.shop_id else False,
        }
        return {
            'name': 'Monthly Sales Report',
            'type': 'ir.actions.client',
            'tag': 'open_sales_monthly_dashboard_report_view',
            'context': action_context,
            'target': 'main'
        }

    @api.constrains('from_date', 'to_date')
    def check_date_range(self):
        if self.to_date and self.from_date:
            if datetime.strptime(str(self.to_date), "%Y-%m-%d") < datetime.strptime(str(self.from_date), "%Y-%m-%d"):
                raise Warning(_("End Date should be grater than Start Date."))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
