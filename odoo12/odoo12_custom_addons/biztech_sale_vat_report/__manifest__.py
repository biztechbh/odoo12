{
    'name': 'Sale VAT Report',
    'version': '1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Point of Sale',
    'summary': 'Sale VAT Report',
    'description': " This module use mainly to print the sales reports of pos orders ",
    'website': 'http://www.acespritech.com',
    'depends': ['point_of_sale', 'flexipharmacy'],
    # 'images': ['static/description/icon.png'],
    'data': [
            'views/report_view.xml',
            'wizard/dashboard_view.xml',
            'wizard/wizard_report.xml',
    ],
    'qweb': [
            'static/src/xml/sale_view.xml',
        ],
    'installable': True,
    'auto_install': False,
}
