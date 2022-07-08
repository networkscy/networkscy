# -*- coding: utf-8 -*-
{
    'name': "KNC Customizations Addon",
    'summary': "KNC Custom Module for Customizations",
    'description': "KNC Custom Module for Customizations",
    'author': "KNC Advanced Lighting",
    'website': "http://www.knc.com.cy",
    'category': "Extra Tools",
    'version': "1.0.0",
    "license": "AGPL-3",

    'depends': [
       'contacts'
    ],

    'data': [
        # Security Rules
        'security/ir.model.access.csv',

        # Views
        'views/partner.xml',
        'views/partner_names.xml',
        'views/partner_profiles.xml',
        'views/partner_relations.xml',
        'views/partner_street_names.xml',
        # 'views/opportunity.xml',
        # 'views/x_product_attribute_value_supplier.xml',

        # Views Website
        # 'views/web_product_template.xml',

        # Menu

        # Reports

        # Reports Configuration
    ],

    'images': [
        'images/KNC_Logo.png',
        'images/KNC_Logo_Inv.png',
        'images/KNC_Logo_Mono.png',
        'images/KNC_Vector.png',
        'images/KNC_Vector_Grey.png',
        'images/KNC_Vector_Mono.png',
        'images/KNC_Letter_Header.jpg',
        'images/KNC_Letter_Footer.jpg',
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'sequence': 0,
    'installable': True,
    'application': True,
    'auto_install': False,
}
