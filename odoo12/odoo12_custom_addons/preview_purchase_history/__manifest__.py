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
{
    'name': 'Preview Purchase History',
    'version': '1.0',
    'category': 'Purchase',
    'summary': 'Show the history of last purchase order',
    'description': """
This module is to display history of last purchase order of particular product.
""",
    # 'price': 15.00,
    # 'currency': 'EUR',
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "http://www.acespritech.com",
    'depends': ['base', 'purchase','biztech_purchase_bonus_qty'],
    'data': [
        'views/purchase_order_line_inherit.xml',
        'wizard/purchase_history_wizard_view.xml',
    ],
    'demo': [],
    # 'images': ['static/description/main_screenshot.png'],
    # 'qweb': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
