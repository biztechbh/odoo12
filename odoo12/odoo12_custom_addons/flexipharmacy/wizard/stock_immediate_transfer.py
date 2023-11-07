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

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        if self._context.get('validate_pickings'):
            pick_to_backorder = self.env['stock.picking']
            pick_to_do = self.env['stock.picking']
            for picking in self.pick_ids:
                # If still in draft => confirm and assign
                if picking.state == 'draft':
                    picking.action_confirm()
                    if picking.state != 'assigned':
                        picking.action_assign()
                        if picking.state != 'assigned':
                            raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                    for move_line in move.move_line_ids.filtered(lambda x: x.picking_id and x.qty_done <= 0):
                        if not move_line.picking_id:
                            move_line.picking_id = move.picking_id.id
                        move_line.qty_done = move_line.product_uom_qty
                if picking._check_backorder():
                    pick_to_backorder |= picking
                    continue
                pick_to_do |= picking
            # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
            if pick_to_do:
                pick_to_do.action_done()
            if pick_to_backorder:
                return pick_to_backorder.action_generate_backorder_wizard()
            return False
        else:
            return super(StockImmediateTransfer, self).process()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
