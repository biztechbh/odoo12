
{
    'name': 'POS Hourly Sales Report',
    'version': '12.0',
    'summary': "POS Hourly Sales Reports",
    'sequence': 16,
    'description': """  POS Hourly Sales Reports""",
    'category': 'sales',
    'author': 'Biztech Computer',
    'maintainer': 'Biztech Computer',
    'website': 'https://biztechbh.biz',
    "depends": ['point_of_sale'],
    "data": [
        'views/report_view.xml',
        'wizard/dashboard_view.xml',
        'wizard/wizard_report.xml',
    ],
    'qweb': [
        'static/src/xml/sale_view.xml',
    ],
    'license': 'AGPL-3',
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

