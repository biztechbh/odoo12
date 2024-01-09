

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime, date


class WizardSalesDashboardReport(models.TransientModel):
    _name = 'wizard.hourly.sales.dashboard.report'

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
            'shop_id': self.shop_id.id
        }
        return {
            'name': 'Hourly Sales Report',
            'type': 'ir.actions.client',
            'tag': 'open_hourly_sales_report_view',
            'context': action_context,
            'target': 'main'
        }

    @api.constrains('from_date', 'to_date')
    def check_date_range(self):
        if self.to_date and self.from_date:
            if datetime.strptime(str(self.to_date), "%Y-%m-%d") < datetime.strptime(str(self.from_date), "%Y-%m-%d"):
                raise ValidationError(_("End Date should be grater than Start Date."))


