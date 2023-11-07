from odoo import api, fields, models, _

class purchase_history_wizard(models.TransientModel):
    _name = 'purchase.history.wizard'

    preview_history = fields.Many2many('purchase.order.line', string='History')
