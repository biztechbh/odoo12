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
    "name": "Product Sales Profit Report",
    "summary": "Product Sales Profit Report",
    "category": "General",
    "version": "1.0.6",
    "author": "Acespritech Solutions Pvt. Ltd.",
    "website": "http://www.acespritech.com",
    "description": """Show Product Sales Profit Report""",
    "depends": ['point_of_sale', 'flexipharmacy'],
    "data": [
        'views/report_view.xml',
        'wizard/dashboard_view.xml',
        'wizard/wizard_report.xml',
        'wizard/update_pos_order_wiz.xml',
        'views/pos_order_view.xml',
    ],
    'qweb': [
        'static/src/xml/sale_view.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,

}
#################################################################################

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
