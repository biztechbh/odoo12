# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import Warning

class UpdatePOSOrder(models.TransientModel):
    _name = 'update.pos.order.wiz'
    _description = "Update POS Order Wizard"
    
    limit = fields.Integer(string="Limit")
    pos_order_id = fields.Many2one('pos.order',string="POS Order")
    single_pos = fields.Boolean(string="Update By Order")
    
    @api.multi
    def update_old_pos_action(self):
        for rec in self:
            if rec.limit:
                pos_line_ids = self.env['pos.order.line'].search([('cost_price_updated', '!=', True)],limit=rec.limit)
                if pos_line_ids:
                    for pos_rec in pos_line_ids:
#                         new_cost = 0
                        new_cost = pos_rec.product_id.uom_id._compute_price(pos_rec.product_id.standard_price,pos_rec.uom_id)
                        cost = new_cost * pos_rec.qty
                        total_sale = pos_rec.price_subtotal
                        profit_amt = total_sale - cost
                        profit_percent = (((total_sale - cost) * 100) / cost) if cost != 0 else 100
                        
                        pos_rec.write({
                            'cost_price': new_cost or 0.00,
                            'cost_price_updated': True,
                            'profit_amount': profit_amt,
                            'profit_percentage': profit_percent,
                            })
                        
#                         cost_price = new_cost
#                         pos_rec.cost_price_updated = True
                else:
                    raise Warning('All POS Order Lines Cost Are Updated')
                
            elif rec.pos_order_id:
                for line in rec.pos_order_id.lines:
                    new_cost = line.product_id.uom_id._compute_price(line.product_id.standard_price,line.uom_id)
                    cost = float("%0.3f" % new_cost) * line.qty
                    total_sale = line.price_subtotal
                    profit_amt = total_sale - cost
                    profit_percent = (((total_sale - cost) * 100) / cost) if cost != 0 else 100
                    line.write({
                            'cost_price': new_cost or 0.00,
                            'cost_price_updated': True,
                            'profit_amount': profit_amt,
                            'profit_percentage': profit_percent
                            })
                    
                    
#                     line.cost_price = new_cost 
#                     line.cost_price_updated = True
#                         if pos_rec.pack_lot_ids:
#                             move_id = self.env['stock.move.line'].search(['&', ('lot_id.name', '=', pos_rec.pack_lot_ids[0].lot_name), ('product_id.product_tmpl_id.id', '=', pos_rec.product_id.product_tmpl_id.id)])
#                             if move_id:
#                                 pos_rec.cost_price = round(move_id[0].move_id.price_unit, 3)
#                             else:
#                                 pos_rec.cost_price = new_cost
#                         else:
#                             pos_rec.cost_price = new_cost
                            
#                 pos_rec.cost_price_updated = True
                
                        