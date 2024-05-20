# -*- coding: utf-8 -*-

import math
import re
from odoo import api, models, fields


class BarcodeWizard(models.TransientModel):
    _name = 'barcode.wizard'
    _description = 'barcode wizard'
    _rec_name = 'barcode'

    barcode = fields.Char(string='Barcode')
    product_id = fields.Many2one('product.template')

    def barcode_update(self):
        if self.barcode:
            self.product_id.barcode = self.barcode

    def barcode_action(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "barcode.wizard",
            "views": [[False, "form"]],
            "target": "new",
            "context": {
                'default_barcode': self.barcode,
                'default_product_id': self.id
            },
        }


class ProductAutoBarcode(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        res = super(ProductAutoBarcode, self).create(vals)
        ean = generate_ean(str(res.id))
        res.barcode = ean
        return res

    # @api.multi
    # def write(self, values):
    #     ean = generate_ean(str(self.product_tmpl_id.id))
    #     values['barcode'] = ean
    #     return super(ProductAutoBarcode, self).write(values)


@api.multi
def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if
    the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


def generate_ean(ean):
    """Creates and returns a valid ean13 from an invalid one"""
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:13]
    if len(ean) < 13:
        ean = ean + '0' * (13 - len(ean))
    return ean[:-1] + str(ean_checksum(ean))


class ProductAutoBarcodeInherit(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        res = super(ProductAutoBarcodeInherit, self).create(vals)
        ean = generate_ean(str(res.id))
        res.barcode = ean
        return res

    # @api.multi
    # def write(self, values):
    #     ean = generate_ean(str(self.id))
    #     values['barcode'] = ean
    #     return super(ProductAutoBarcodeInherit, self).write(values)