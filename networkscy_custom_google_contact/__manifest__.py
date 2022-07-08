# -*- coding: utf-8 -*-
{
    'name': "Odoo Google Contacts Connector",
    'summary': """Google App (Contacts) Integration with ODOO.""",
    'description': """
        Synchronization of ODOO with Google Apps.
        Once data created in Google account, will be reflected in ODOO by justone click.
    """,
    'author': "WoadSoft",
    'website': "https://woadsoft.com/",
    'category': "Extra Tools",
    'version': '1.0',
    'depends': ['base', 'contacts', 'networkscy_custom_addon'],
    'data': [
        'security/ir.model.access.csv',
        'views/credential_views.xml',
        'views/connector_views.xml',
        'views/import_views.xml',
        'views/export_views.xml',
        'views/contact_views.xml',
        'views/cron_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'external_dependencies': {
        'python': [],
    },
    'price': 150,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ["images/banner.gif"],
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
}
