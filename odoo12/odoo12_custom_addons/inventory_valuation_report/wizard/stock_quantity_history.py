# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'
    _description = 'Stock Quantity History'

    location_ids = fields.Many2many('stock.location', string="Locations")

    def download_pdf(self):
        if self.compute_at_date:
            products = self.env['product.product'].with_context(to_date=self.date).search([('type', '=', 'product'), ('qty_available', '!=', 0)])
        else:
            products = self.env['product.product'].search([('type', '=', 'product'), ('qty_available', '!=', 0)])
        location_list = []
        if self.location_ids:
            for location in self.location_ids:
                stock_quants = self.env['stock.quant'].search_read(domain=[('location_id', '=', location.id), ('product_id', 'in', products.ids)], fields=['product_id', 'quantity'])
                location_list.append({
                    'location_id': location.ids,
                    'products': [{'product_id': quant.get('product_id')[0], 'qty': quant.get('quantity')} for quant in stock_quants],
                })
        else:
            stock_quants_location = self.env['stock.quant'].search_read(
                domain=[('product_id', 'in', products.ids)],
                fields=['location_id'])
            location_ids = list(map(lambda quant: quant.get('location_id') and quant.get('location_id')[0], stock_quants_location))
            location_ids = list(set(location_ids))
            for location in location_ids:
                stock_quants = self.env['stock.quant'].search_read(
                    domain=[('location_id', '=', location), ('product_id', 'in', products.ids)],
                    fields=['product_id', 'quantity'])
                location_list.append({
                    'location_id': [location],
                    'products': [{'product_id': quant.get('product_id')[0], 'qty': quant.get('quantity')} for quant in
                                 stock_quants],
                })
        data = {
            'id': self.ids,
            'location_list': location_list
        }
        return self.env.ref('inventory_valuation_report.action_report_stock_valuation').report_action(self.ids, data=data)


    def open_table(self):
        self.ensure_one()
        action = super(StockQuantityHistory, self).open_table()
        if self.location_ids:
            context = action.get('context')
            context = context or {}

        tree_view_id = self.env.ref('stock.view_stock_quant_tree').id
        form_view_id = self.env.ref('stock.view_stock_quant_form').id
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Products'),
            'res_model': 'stock.quant',
            'domain': "[('location_id','in',%s)]"%(self.location_ids.ids),
            'context': dict(self.env.context, to_date=self.date,group_by='location_id'),
        }


        # if self.location_ids:
        #     domain = "('location_id','in',%s)"%(self.location_ids.ids)
        #
        # # action['domain'] = action.get('domain')[:-1] + "," + domain + ']'
        # # action['domain']  = "['&','&'," + action['domain'][1:]
        # if action.get('domain',False):
        #     stock_quants = self.env['stock.quant'].search(
        #         [('location_id', 'in', self.location_ids.ids), ('quantity', '!=', 0)]).mapped('product_id')
        #     # stock_quants = self.env['stock.quant'].search(
        #     #     [('location_id', 'in', self.location_ids.ids)]).mapped('id')
        #     # action['domain'] = "['&','|',('type', '=', 'product'), ('qty_available', '!=', 0),('id','in',%s)]"%(stock_quants)
        #     action['domain'] = "[('id','in',%s)]"%(stock_quants.ids)
        return action