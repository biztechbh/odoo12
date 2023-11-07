# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
{
    "name": "Multiple Purchase Order Lines set for the barcode print",
    "summary": "Multiple Purchase Order Lines set for the barcode print",
    "category": "General",
    "version": "1.0.0",
    "author": "Acespritech Solutions Pvt. Ltd.",
    "website": "http://www.acespritech.com",
    "description": """Multiple Purchase Order Lines set for the barcode print""",
    "depends": ['aspl_product_small_label_zebra', 'aspl_product_small_label_zebra', 'biztech_purchase_bonus_qty'],
    "data": [
        'wizard/wizard_po_line_for_barcode_view.xml',
        'views/purchase_order_print.xml',
    ],
    'qweb': [
    ],
    "application": True,
    "installable": True,
    "auto_install": False,

}
#################################################################################

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
