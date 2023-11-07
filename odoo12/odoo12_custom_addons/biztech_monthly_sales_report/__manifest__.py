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
    'name': 'POS Monthly Sales Report',
    'summary': 'Custom POS Monthly Sales Report Dashboard',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'category': 'General',
    'version': '1.0',
    'depends': [
        'base', 'flexipharmacy','point_of_sale',
    ],
    'data': [
        'views/report_view.xml',
        'wizard/monthly_dashboard_view.xml',
        'wizard/wizard_report.xml',
    ],
    'qweb': [
        'static/src/xml/sale_view.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
