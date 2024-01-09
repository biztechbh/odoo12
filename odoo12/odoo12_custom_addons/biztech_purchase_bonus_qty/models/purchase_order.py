from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import timedelta
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_round
from odoo.tools.float_utils import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    bonus_qty = fields.Float('Bonus Quantity', digits=dp.get_precision('Product Unit of Measure'))
    new_price_unit = fields.Float('New Unit Price', store=True, digits=dp.get_precision('Product Price'))
    date_expire = fields.Datetime(string='Expiry Date')
    lot_number = fields.Char('Lot/Serial Number')
    price_unit = fields.Float(string='Unit Price',  store=True,required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Float(string='Subtotal')



    # @api.depends('price_subtotal', 'bonus_qty', 'product_qty', 'taxes_id')
    # def _compute_new_amount(self):
    #     for line in self:
    #         if line.price_subtotal:
    #             line.update({
    #                 'price_unit': line.price_subtotal / line.product_qty,
    #                 'new_price_unit': line.price_subtotal / (line.product_qty + line.bonus_qty) if line.bonus_qty > 0 else False,
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
    #             line.product_uom_qty = line.product_uom._compute_quantity((line.product_qty + line.bonus_qty), line.product_id.uom_id)
    #         else:
    #             line.product_uom_qty = line.product_qty + line.bonus_qty

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'new_price_unit': self.new_price_unit,
            'bonus_qty': self.bonus_qty,
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

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
            new_cost = rec.product_id.uom_id._compute_price(rec.product_id.standard_price,rec.uom_id)
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

    def _prepare_invoice_line_from_po_line(self, line):
        if line.product_id.purchase_method == 'purchase':
            qty = line.product_qty - line.qty_invoiced
        else:
            qty = line.product_qty
        if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
            qty = 0.0
        taxes = line.taxes_id
        invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(taxes, line.product_id,
                                                                        line.order_id.partner_id)
        invoice_line = self.env['account.invoice.line']
        date = self.date or self.date_invoice
        data = {
            'purchase_line_id': line.id,
            'name': line.order_id.name + ': ' + line.name,
            'origin': line.order_id.origin,
            'uom_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id._convert(
                line.price_unit, self.currency_id, line.company_id, date or fields.Date.today(), round=False),
            'quantity': qty,
            'discount': 0.0,
            'account_analytic_id': line.account_analytic_id.id,
            'analytic_tag_ids': line.analytic_tag_ids.ids,
            'invoice_line_tax_ids': invoice_line_tax_ids.ids
        }
        account = invoice_line.with_context(purchase_line_id=line.id).get_invoice_line_account('in_invoice',
                                                                                               line.product_id,
                                                                                               line.order_id.fiscal_position_id,
                                                                                               self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data