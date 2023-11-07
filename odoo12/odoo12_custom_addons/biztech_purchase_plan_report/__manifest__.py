{
    'name': 'Purchase Planning Report',
    'version': '1.0',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Purchase',
    'summary': 'Purchase Planning Report',
    'description': " This module use mainly to print the purchase planning reports of purchase orders ",
    'website': 'http://www.acespritech.com',
    'depends': ['point_of_sale', 'flexipharmacy', 'purchase'],
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
