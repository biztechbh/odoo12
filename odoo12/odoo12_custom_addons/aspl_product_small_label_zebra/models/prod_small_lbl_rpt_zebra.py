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

from odoo import models, api, _
from reportlab.graphics.barcode import createBarcodeDrawing
from base64 import b64encode
from odoo.exceptions import Warning


class prod_small_label_zebra(models.AbstractModel):
    _name = 'report.aspl_product_small_label_zebra.prod_small_label_zebra'
    _description = 'report.aspl_product_small_label_zebra.prod_small_label_zebra'

    def _get_style(self, data):
        return 'height:' + str(data['form']['display_height']) + 'px;width:' + str(data['form']['display_width']) + 'px;'

    def _get_barcode_string(self, value, type, data):
        encoded_string = ''
        if data['form']['with_barcode'] and value and type:
            try:
                encoded_string = createBarcodeDrawing(type, value=value, format='png', width=int(data['form']['barcode_height']),
                                                             height=int(data['form']['barcode_width']),
                                                             humanReadable=data['form']['humanReadable'])
            except Exception:
                return ''
            encoded_string = b64encode(encoded_string.asString('png'))
        return encoded_string

    def _get_barcode_data(self, data):
        product_list = []
        product_ids = self.env['product.small.label.qty'].search([('id', 'in', data['form']['product_ids'])])
        if data.get('form').get('label_preview'):
            product_ids = product_ids[0]
            product_ids.write({'qty': 1})
        for product_line in product_ids:
            if product_line.line_id:
                line_brw = self.env[model].browse(product_line.line_id)
                for qty in range(product_line.qty):
                    product_list.append(line_brw)
            else:
                for qty in range(product_line.qty):
                    price = 0.000

                    if product_line.stock_production_lot_id:
                        price_unit = round(product_line.product_id.lst_price * (1 - (0.0) / 100.0),3)
                        taxes = product_line.product_id.taxes_id.compute_all(price_unit, self.env.user.company_id.currency_id, 1,
                                                                          product_line.product_id, self.env.user.partner_id)['taxes']
                        currency_id = self.env.user.company_id.currency_id
                        if taxes:
                            for each in taxes:
                                price += each['amount'] + each['base']
                        else:
                            price = price_unit

                        barcode = str(product_line.product_id.barcode) + str(product_line.stock_production_lot_id.name)
                        barcode_str = str(product_line.product_id.barcode) +"-"+ str(product_line.stock_production_lot_id.name)
                        lot = product_line.stock_production_lot_id.name
                        product_list.append(
                            {'product_id': product_line.product_id, 'barcode': barcode, 'lot': lot, 'price': price,
                             'barcode_str': barcode_str, 'currency_id': currency_id})
                    else:
                        barcode = str(product_line.product_id.barcode)
                        lot = 000
                        currency_id = self.env.user.company_id.currency_id
                        product_list.append(
                            {'product_id': product_line.product_id, 'barcode': barcode, 'lot': lot, 'price': price,
                             'barcode_str': barcode, 'currency_id': currency_id})
        return product_list

    def _get_price(self, product, pricelist_id=None):
        price = 0
        if product:
            price = product.list_price
            if pricelist_id:
                price = pricelist_id.price_get(product.id, 1.0)
                if price and isinstance(price, dict):
                    price = price.get(pricelist_id.id)
        return price

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('aspl_product_small_label_zebra.prod_small_label_zebra')
        conpany_name=self.env.user.company_id.name
        return {
            'doc_ids': self.env["wizard.product.small.label.report"].browse(data["ids"]),
            'doc_model': "wizard.product.small.label.report",
            'docs': self,
            'get_barcode_data': self._get_barcode_data,
            'get_barcode_string': self._get_barcode_string,
            'get_price': self._get_price,
            'get_style' : self._get_style,
            'data': data,
            'company':conpany_name.upper(),
            'price':'Price',
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
