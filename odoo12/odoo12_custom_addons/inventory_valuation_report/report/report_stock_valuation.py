# -*- coding: utf-8 -*-

from odoo import api, models, _


class ReportStockValuation(models.AbstractModel):
    _name = "report.inventory_valuation_report.report_stock_valuation"
    _description = "Report Stock Valuation"

    @api.model
    def _get_report_values(self, docids, data=None):
        docids = self.env['stock.quantity.history'].browse(data.get('id', []))
        location_list = data.get('location_list')
        new_list = []
        for l in location_list:
            for item in l.get('products'):
                item['product_id'] = self.env['product.product'].browse(item.get('product_id'))
            new_list.append({
                'location_id': self.env['stock.location'].browse(l.get('location_id')),
                'products': l.get('products')
            })
        return {
            'docs': docids,
            'location_list': new_list,
        }
