from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import timedelta
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.tools.float_utils import float_compare
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    bonus_qty = fields.Float('Bonus Quantity', digits=dp.get_precision('Product Unit of Measure'))
    new_price_unit = fields.Float('New Unit Price', compute='_compute_new_amount', store=True,
                                  digits=dp.get_precision('Product Price'))
    date_expire = fields.Datetime(string='Expiry Date')
    lot_number = fields.Char('Lot/Serial Number')
    price_unit = fields.Float(string='Unit Price', required=True,
                              digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float(string='Subtotal', store=True)
    total_qty = fields.Float("Total Quantity", store=True, compute='_compute_total_quantity')
    sl_no = fields.Integer(string='Sl. No.', compute='_compute_serial_number')

    @api.depends('sequence', 'order_id')
    def _compute_serial_number(self):
        for order_line in self:
            serial_no = 1
            for line in order_line.mapped('order_id').order_line:
                if line.product_id:
                    line.sl_no = serial_no
                    serial_no += 1
                else:
                    line.sl_no = 0

    @api.depends('bonus_qty', 'product_qty')
    def _compute_total_quantity(self):
        for line in self:
            line.total_qty = (line.bonus_qty + line.product_qty)

    @api.depends('bonus_qty')
    def _compute_new_amount(self):
        for line in self:
            if line.bonus_qty:
                line.update({
                    'price_unit': line.price_subtotal / line.product_qty,
                    'new_price_unit': line.price_subtotal / (
                            line.product_qty + line.bonus_qty) if line.bonus_qty > 0 else False,
                })

    # @api.depends('price_subtotal', 'bonus_qty', 'product_qty', 'taxes_id')
    # def _compute_new_amount(self):
    #     for line in self:
    #         if line.price_subtotal:
    #             line.update({
    #                 'price_unit': line.price_subtotal / line.product_qty,
    #                 'new_price_unit': line.price_subtotal / (
    #                             line.product_qty + line.bonus_qty) if line.bonus_qty > 0 else False,
    #             })

    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     for line in self:
    #         if not line.product_id.taxes_id:
    #             line.update({
    #                 'taxes_id': [(5, 0, 0)]
    #             })
    #         vals = line._prepare_compute_all_values()
    #         taxes = line.taxes_id.compute_all(
    #             vals['price_unit'],
    #             vals['currency_id'],
    #             vals['product_qty'],
    #             vals['product'],
    #             vals['partner'])
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #         })
    #
    # @api.multi
    # @api.depends('product_uom', 'product_qty', 'bonus_qty', 'product_id.uom_id')
    # def _compute_product_uom_qty(self):
    #     for line in self:
    #         if line.product_id.uom_id != line.product_uom:
    #             line.product_uom_qty = line.product_uom._compute_quantity((line.product_qty + line.bonus_qty),
    #                                                                       line.product_id.uom_id)
    #         else:
    #             line.product_uom_qty = line.product_qty + line.bonus_qty
    # #
    # def _prepare_compute_all_values(self):
    #     # Hook method to returns the different argument values for the
    #     # compute_all method, due to the fact that discounts mechanism
    #     # is not implemented yet on the purchase orders.
    #     # This method should disappear as soon as this feature is
    #     # also introduced like in the sales module.
    #     self.ensure_one()
    #     return {
    #         'new_price_unit': self.new_price_unit,
    #         'bonus_qty': self.bonus_qty,
    #         'price_unit': self.price_unit,
    #         'currency_id': self.order_id.currency_id,
    #         'product_qty': self.product_qty,
    #         'product': self.product_id,
    #         'partner': self.order_id.partner_id,
    #     }

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for line in res:
            line['date_expire'] = self.date_expire
            lot_id = self.env['stock.production.lot'].search(
                [('name', '=', self.lot_number), ('product_id', '=', self.product_id.id)])
            if lot_id:
                raise Warning('Please Add Unique Lot Number for %s' % (self.product_id.name))
            else:
                line['lot_number'] = self.lot_number
            product = self.env['product.product'].search([('id', '=', line['product_id'])])
            line.update({
                'price_unit': round(self.new_price_unit, 3) or round(self.price_unit, 3),
                'date_expire': self.date_expire, 'lot_number': self.lot_number,
                'product_uom_qty': line['product_uom_qty'] + self.bonus_qty,
            })
            if product.categ_id.property_cost_method == 'standard':
                product.write({'standard_price': line['price_unit']})
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    cost_price = fields.Float("Cost", compute='compute_cost_price', store=True, digits=dp.get_precision('Product Price'))

    @api.depends('pack_lot_ids')
    def compute_cost_price(self):
        for rec in self:
            new_cost = rec.product_id.uom_id._compute_price(rec.product_id.standard_price, rec.uom_id)
            rec.cost_price = new_cost
#             if rec.pack_lot_ids:
#                 move_id = self.env['stock.move.line'].search(['&', ('lot_id.name', '=', rec.pack_lot_ids[0].lot_name), ('product_id.product_tmpl_id.id', '=', rec.product_id.product_tmpl_id.id)])
#                 if move_id:
#                     rec.cost_price = round(move_id[0].move_id.price_unit, 3)
#                 else:
#                     rec.cost_price = new_cost
# #                     rec.cost_price = round(rec.product_id.standard_price, 3)
#             else:
#                 rec.cost_price = new_cost
#                 rec.cost_price = round(rec.product_id.standard_price, 3)


class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_number = fields.Char('Lot/Serial Number')
    date_expire = fields.Datetime(string='Expiry Date')

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        if self.picking_type_id.code == 'incoming':
            res['lot_name'] = self.lot_number
            res['qty_done'] = self.product_uom_qty
        return res

    @api.multi
    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            line = self.purchase_line_id
            order = line.order_id
            if line.new_price_unit:
                price_unit = line.new_price_unit
            else:
                price_unit = line.price_unit
            if line.taxes_id:
                price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_excluded']
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                # The date must be today, and not the date of the move since the move move is still
                # in assigned state. However, the move date is the scheduled date until move is
                # done, then date of actual move processing. See:
                # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
            return price_unit
        return super(StockMove, self)._get_price_unit()


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for rec in self:
            if rec.exists():
                rec.lot_id.write({'life_date': rec.move_id.date_expire})
        return res


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    bonus_qty = fields.Float('Bonus Quantity', digits=dp.get_precision('Product Unit of Measure'))

    def _prepare_invoice_line_from_po_line(self, line):
        vals = super()._prepare_invoice_line_from_po_line(line)
        vals['quantity'] = line.product_qty
        vals['bonus_qty'] = abs(line.qty_received - line.product_qty)
        return vals


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('state', 'order_line.qty_invoiced', 'order_line.qty_received', 'order_line.product_qty')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done'):
                order.invoice_status = 'no'
                continue

            if any(float_compare(line.qty_invoiced,
                                 line.product_qty if line.product_id.purchase_method == 'purchase' else line.product_qty,
                                 precision_digits=precision) == -1 for line in order.order_line):
                order.invoice_status = 'to invoice'
            elif all(float_compare(line.qty_invoiced,
                                   line.product_qty if line.product_id.purchase_method == 'purchase' else line.qty_invoiced,
                                   precision_digits=precision) >= 0 for line in order.order_line) and order.invoice_ids:
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'

