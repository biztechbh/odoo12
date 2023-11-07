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
    "name": "Inventory Valuation Report",
    "summary": "Inventory Valuation Report",
    "category": "General",
    "version": "1.0.0",
    "description": """Inventory Valuation Report""",
    "depends": ['stock_account','stock_inventory_valuation_location','stock'],
    "data": [
        'report/report_stock_valuation.xml',
        'report/report_views.xml',
        'wizard/stock_quantity_history_view.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,

}
#################################################################################

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
