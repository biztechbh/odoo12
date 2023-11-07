# -*- coding: utf-8 -*-
#################################################################################
# Author : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import models, fields, api, _

class DoneReadyPicking(models.TransientModel):
    _name = 'done.ready.picking'

    picking_ids = fields.Many2many('stock.picking', 'stock_picking_done_rel')

    @api.model
    def default_get(self, default_fields):
        res = super(DoneReadyPicking, self).default_get(default_fields)
        picking_lst = []
        pos_orders = self.env['pos.order'].search([('picking_id.state', '=', 'assigned')], limit=500)
        for pos in pos_orders:
            picking_lst.append(pos.picking_id.id)
        if picking_lst:
            res['picking_ids'] = [(6, 0, picking_lst)]
        return res

    @api.multi
    def action_done_ready_picking(self):
        non_done_pick = []
        for pick in self.picking_ids:
            if pick.move_lines:
                if len(pick.move_line_ids) > 1:
                    if pick.move_lines.filtered(lambda l: l.reserved_availability == 0.0):
                        for line in pick.move_line_ids:
                            product = line.product_id
                            if product and product.tracking != 'none':
                                if not line.lot_name and not line.lot_id:
                                    line.lot_name = '123-' + str(line.id)
                                if not line.qty_done:
                                    qty = line.product_uom_qty
                                    line.qty_done = qty
                        immediate_transfer = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick.id)]})
                        immediate_transfer.process()
                    else:
                        for line in pick.move_line_ids:
                            product = line.product_id
                            if product and product.tracking != 'none':
                                if not line.lot_name and not line.lot_id:
                                    line.lot_name = '123-' + str(line.id)
                                if not line.qty_done:
                                    qty = line.product_uom_qty
                                    line.qty_done = qty
                        immediate_transfer = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick.id)]})
                        immediate_transfer.process()
                else:
                    if pick.move_lines.filtered(lambda l: l.reserved_availability == 0.0):
                        non_done_pick.append(pick.id)
                    else:
                        for line in pick.move_line_ids:
                            product = line.product_id
                            if product and product.tracking != 'none':
                                if not line.lot_name and not line.lot_id:
                                    line.lot_name = '123-' + str(line.id)
                                    immediate_transfer = self.env['stock.immediate.transfer'].create(
                                        {'pick_ids': [(4, pick.id)]})
                                    immediate_transfer.process()
                            if not line.qty_done:
                                qty = line.product_uom_qty
                                line.qty_done = qty
                                immediate_transfer = self.env['stock.immediate.transfer'].create(
                                    {'pick_ids': [(4, pick.id)]})
                                immediate_transfer.process()
                            if line.lot_id and line.lot_id.product_qty < 0.0:
                                line.lot_name = '123-' + str(line.id)
                                immediate_transfer = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, pick.id)]})
                                immediate_transfer.process()