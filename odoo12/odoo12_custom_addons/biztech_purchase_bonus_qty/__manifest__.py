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
    "name": "Purchase Bonus Quantity",
    "summary": "Purchase Bonus Quantity",
    "category": "Purchase",
    "version": "1.0.2",
    "author": "Acespritech Solutions Pvt. Ltd.",
    "website": "http://www.acespritech.com",
    "description": """Show Purchase Bonus Quantity""",
    "depends": ['purchase', 'stock', 'purchase_stock', 'point_of_sale'],
    "data": [
            'views/purchase_bonus_qty_view.xml'
    ],
    'qweb': [
        # 'static/src/xml/sale_view.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,

}
#################################################################################

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
