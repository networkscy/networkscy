# -*- coding: utf-8 -*-
{
    'name': "Networkscy Customizations Addon",
    'summary': "Networkscy Custom Module for Customizations",
    'description': "Networkscy Custom Module for Customizations",
    'author': "Networkscy",
    'website': "http://www.networkscy.com",
    'category': "Extra Tools",
    'version': "1.0.0",
    "license": "AGPL-3",

    'depends': [
        'base', 'contacts', 'base_address_city', 'base_location',
    ],

    'data': [
        # Security Rules

        # Views
        'views/partner_street_names.xml',
        'views/partner.xml',
        



        # Menu


        # Reports


        # Reports Configuration
    ],

    'images': [
     #   'images/KNC_Logo.png',
     
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'sequence': 0,
    'installable': True,
    'application': True,
    'auto_install': False,
}
