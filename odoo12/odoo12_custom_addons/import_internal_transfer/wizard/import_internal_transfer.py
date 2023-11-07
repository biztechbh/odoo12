# -*- coding: utf-8 -*-

import base64
import csv
import io
from odoo.exceptions import ValidationError
from odoo import api, fields, models


class StockInternalTransfer(models.TransientModel):

    _name = 'stock.internal.transfer'
    _description = 'Stock Internal Transfer'

    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type', required=True, domain=[('code', '=', 'internal')])
    import_file = fields.Binary('Import File')
    location_id = fields.Many2one('stock.location', "Source Location", required=True)
    location_dest_id = fields.Many2one('stock.location', "Destination Location", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('stock.picking'),required=True)
    auto_validate = fields.Boolean('Auto Validate')

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            self.location_id = self.picking_type_id.default_location_src_id.id
            self.location_dest_id = self.picking_type_id.default_location_dest_id.id

    def _create_picking(self):
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
        })
        return picking

    def _create_stock_moves(self, values, picking):
        product = self.env['product.product'].search(
            [('name', '=', values.get('product'))], limit=1)
        if not product:
            raise ValidationError("Product %s not available in system" % (values.get('product')))
        move = self.env['stock.move'].search([('product_id', '=', product.id), ('picking_id', '=', picking.id)], limit=1)
        if move:
            # qty = move.product_uom_qty
            qty = float(values.get('qty',0))
            move.product_uom_qty = move.product_uom_qty + qty
            return move
        move = self.env['stock.move'].create({
            'picking_type_id': self.picking_type_id.id,
            'picking_id': picking.id,
            'reference': picking.name,
            'name': picking.name,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': values.get('qty'),
            'location_dest_id': self.location_dest_id.id,
            'location_id': self.location_id.id,
        })
        if move:
            return move
        else:
            raise ValidationError("Move not created due to some problem. Product: %s" %(values.get('product')))

    def set_expiry_on_lots(self,lot_id):
        if not lot_id.purchase_order_ids:
            return
        purchase_order_id = lot_id.purchase_order_ids[0]
        if purchase_order_id:
            pid = lot_id.product_id
            orderlines = purchase_order_id.order_line.filtered(lambda l : l.product_id.id == pid.id)
            if orderlines:
                ol = orderlines[0]
                lot_id.life_date = ol.date_expire


    def import_csv(self):
        if self.import_file:
            keys = ['product', 'qty', 'lot']
            csv_data = base64.b64decode(self.import_file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)
            values = {}
            picking = self._create_picking()
            picking.move_type = 'direct'
            # picking.is_locked = False
            if not picking:
                raise ValidationError('Due to some problem Picking not created!')
            counter = 0
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        move = self._create_stock_moves(values, picking)

                        if move:
                            picking.action_confirm()
                            # picking.action_assign()

                            # if picking.show_check_availability:
                            #     raise ValidationError("Please check stock available in select location!")

                            if move.product_id.tracking == 'lot':
                                # if move.product_id.with_context(location=self.location_id.id).qty_available < move.product_uom_qty:
                                    # raise ValidationError("Please check available stock in '%s' location for the product: '%s' (Row No: %s)!" % (self.location_id.display_name, move.product_id.name, i+1))
                                    # if len(move.move_line_ids) == 0:
                                if True or not move.move_line_ids:
                                    # move.product_uom_qty = float(values.get('qty', 0))
                                    # move.write({'product_uom_qty': float(values.get('qty', 0))})
                                    vals = {
                                        'move_id': move.id,
                                        'location_id': move.location_id.id,
                                        'location_dest_id': move.location_dest_id.id,
                                        'qty_done': float(values.get('qty', 0)),
                                        # 'product_uom_qty':float(values.get('qty', 0)),
                                        'product_id': move.product_id.id,
                                        'product_uom_id': move.product_uom.id,
                                        'picking_id':picking.id
                                    }

                                    move.move_line_ids = [(0, 0, vals)]
                                    # move_line = self.env['stock.move.line'].create(vals)
                                    move_line = move.move_line_ids[-1]
                                    if not move_line:
                                        raise ValidationError("Move Line not created due to some problem!. Product: %s" % (values.get('product')))

                                if move.move_line_ids:
                                    move_line = move.move_line_ids[-1]

                                    if self.picking_type_id and self.picking_type_id.use_create_lots:
                                        # picking.move_line_ids_without_package[counter].lot_name = values.get('lot', '-')
                                        move_line.lot_name = values.get('lot', '-')
                                    if self.picking_type_id and self.picking_type_id.use_existing_lots:
                                        # product = picking.move_line_ids_without_package[counter].product_id
                                        product = move_line.product_id
                                        lot_id = self.env['stock.production.lot'].search([('product_id', '=', product.id), ('name', '=', values.get('lot', '-'))], limit=1)
                                        if not lot_id:
                                            lot_id = self.env['stock.production.lot'].create({'product_id': product.id, 'name': values.get('lot', '-')})
                                        # picking.move_line_ids_without_package[counter].lot_id = lot_id.id

                                        # set expiry on lots
                                        if not lot_id.life_date:self.set_expiry_on_lots(lot_id)
                                        move_line.date_expire = lot_id.life_date
                                        move_line.lot_id = lot_id.id
                                        move_line.lot_number = lot_id.name

                                        move.date_expire = lot_id.life_date
                                        move_line.lot_id = lot_id.id
                                        move.lot_number = lot_id.name
                                    # picking.move_line_ids_without_package[counter].qty_done = picking.move_line_ids_without_package[counter].product_uom_qty
                                    if move_line.qty_done == 0:
                                        move_line.qty_done = values.get('qty', 0)
                                    counter += 1
                        # move.product_uom_qty = values.get('qty', 0)
            return {
                'name': 'Transfer Order',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'res_id': picking.id,
                'view_mode': 'form',
                'context' :{'product_uom_qty': 3},
                'views': [(False, 'form')],
            }
