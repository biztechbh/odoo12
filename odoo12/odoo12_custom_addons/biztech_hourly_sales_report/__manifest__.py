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
    "name": "Hourly Sales Report",
    "summary": "Hourly Sales Report",
    "category": "General",
    "version": "1.0.0",
    "author": "Acespritech Solutions Pvt. Ltd.",
    "website": "http://www.acespritech.com",
    "description": """Show hourly sales report""",
    "depends": ['point_of_sale', 'flexipharmacy'],
    "data": [
        'views/report_view.xml',
        'wizard/dashboard_view.xml',
        'wizard/wizard_report.xml',
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
