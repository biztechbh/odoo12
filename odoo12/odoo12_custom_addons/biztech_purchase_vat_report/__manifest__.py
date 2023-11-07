{
    'name': 'Purchase VAT Report',
    'version': '1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Point of Sale',
    'summary': 'Purchase VAT Report',
    'description': " This module use mainly to print the purchase reports of purchase orders ",
    'website': 'http://www.acespritech.com',
    'depends': ['point_of_sale', 'flexipharmacy'],
    # 'images': ['static/description/icon.png'],
    'data': [
            'views/report_view.xml',
            'wizard/dashboard_view.xml',
            'wizard/wizard_report.xml',
    ],
    'qweb': [
            'static/src/xml/purchase_view.xml',
        ],
    'installable': True,
    'auto_install': False,
}
