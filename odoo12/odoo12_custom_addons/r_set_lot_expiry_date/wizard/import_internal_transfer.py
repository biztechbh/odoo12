# -*- coding: utf-8 -*-

import base64
import csv
import io
from odoo.exceptions import ValidationError
from odoo import api, fields, models

import logging
import logging.handlers


_logger = logging.getLogger(__name__)

class DoneIds(models.Model):
    _name = "r.done.ids"

    done_lot_id = fields.Integer()


class R_Set_Lot_Expiry_Date(models.TransientModel):

    _name = 'set.lot.expiry.date'
    _description = 'r_set_lot_expiry_date'

    lot_ids = fields.Many2many('stock.production.lot', string='Lots'  )
    res_limit = fields.Integer(string = 'Limit Records')


    def import_csv(self):
        not_in_ids = self.env['r.done.ids'].search([]).mapped('done_lot_id')
        lots = self.env['stock.production.lot'].search(['&',('id','not in',not_in_ids),('life_date','=',False)],limit=self.res_limit)
        # location = self.env['stock.location'].search([('name','=','Al Rabeeh')])
        # wh_stock = self.env['stock.location'].search([('name','=','Stock')])
        # whstk_lots = self.env['stock.quant'].search([('location_id', '=', wh_stock.id)], limit=100).mapped('lot_id')
        # alrab_lots = self.env['stock.production.lot'].search([('location_id','=',location.id)],limit=10000).mapped('lot_id')
        # lots = self.env['stock.production.lot'].search(['&',('id','in',alrab_lots.ids),('life_date', '=', False)], limit=5000)
        # msg = ""
        # have ,nohave = 0 , 0
        count = 0
        for l in lots:
            purchase_order_ids = l.purchase_order_ids
            if purchase_order_ids:
                order_lines = purchase_order_ids.order_line.filtered(lambda ll: ll.product_id == l.product_id)
                order_lines = order_lines[-1]
                l.life_date  = order_lines.date_expire
                _logger.info("purchase orer was their life date updated lot id =%s , product =%s ******************* "%(l.id,l.product_id.name))
                # have += 1
            else:
                _logger.info("purchase order not found lot id =%s , product =%s!!!!"%(l.id,l.product_id.name))
            self.env['r.done.ids'].create({'done_lot_id':l.id})
            count += 1
            if count%10 == 0:
                self.env.cr.commit()
                # h = self.env['stock.production.lot'].search(['&','&',('name','=',l.name),('purchase_order_ids','=',True),('product_id','=',l.product_id.id)])
                # stmv = self.env['stock.move'].search(['&', '&',('location_dest_id','=',location.id),('product_id', '=', l.product_id.id),
                #                                ('lot_number', '=', l.name)])
                # stmv = self.env['stock.move'].search(
                #     ['&',  ('product_id', '=', l.product_id.id),
                #      ('lot_number', '=', l.name)])
                # if stmv:
                #     l.life_date = stmv.date_expire
                #     _logger.info("from stock move life date updated")
                #     have += 1
                # nohave += 1

    # def import_csv(self):
    #
    #     lots = self.env['stock.production.lot'].search([('life_date','=',False)],limit=100)
    #     location = self.env['stock.location'].search([('name','=','Al Rabeeh')])
    #     wh_stock = self.env['stock.location'].search([('name','=','Stock')])
    #     whstk_lots = self.env['stock.quant'].search([('location_id', '=', wh_stock.id)], limit=100).mapped('lot_id')
    #     alrab_lots = self.env['stock.production.lot'].search([('location_id','=',location.id)],limit=10000).mapped('lot_id')
    #     lots = self.env['stock.production.lot'].search(['&',('id','in',alrab_lots.ids),('life_date', '=', False)], limit=5000)
    #     msg = ""
    #     have ,nohave = 0 , 0
    #     for l in lots:
    #         if len(l.purchase_order_ids)>=1:
    #             _logger.info("purchase orer was their life date updated")
    #             l.life_date  = l.purchase_order_ids.order_line.filtered(lambda ll: ll.product_id == l.product_id).date_expire
    #             have += 1
    #         else:
    #             # h = self.env['stock.production.lot'].search(['&','&',('name','=',l.name),('purchase_order_ids','=',True),('product_id','=',l.product_id.id)])
    #             # stmv = self.env['stock.move'].search(['&', '&',('location_dest_id','=',location.id),('product_id', '=', l.product_id.id),
    #             #                                ('lot_number', '=', l.name)])
    #             stmv = self.env['stock.move'].search(
    #                 ['&',  ('product_id', '=', l.product_id.id),
    #                  ('lot_number', '=', l.name)])
    #             if stmv:
    #                 l.life_date = stmv.date_expire
    #                 _logger.info("from stock move life date updated")
    #                 have += 1
    #             nohave += 1



