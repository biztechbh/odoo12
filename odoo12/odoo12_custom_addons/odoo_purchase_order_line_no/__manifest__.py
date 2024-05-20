# -*- coding: utf-8 -*-
{
    'name': 'Serial no for product lines in Purchase Order lines',
    'version': '13.0.0.0',
    'author': 'Cloudroits',
    'summary': 'Add serial/line nos to product lines in Purchase Orders',
    'description': """This module displays serial/line nos to product lines in Purchase Orders both in the form as well in reports.""",
    'category': 'Purchase',
    'website': 'https://www.cloudroits.com/',
    'license': 'AGPL-3',
    'depends': ['sale_management','purchase'],
    'data': [
        'views/purchase_order_views.xml',
        'report/purchase_order_report.xml',
    ],
    'qweb': [],
    'images': ['static/description/odoo_po_line_nos_banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
