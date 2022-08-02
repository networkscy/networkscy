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
        'base', 'contacts', 'base_address_city', 'base_location', 'sale',
    ],

    'data': [
        # Security Rules
         'security/ir.model.access.csv',

        # Views
         'views/partner.xml',
        # views/partner_names.xml',
         'views/partner_profiles.xml',
         # 'views/partner_relations.xml',
         'views/partner_street_names.xml',
         'views/sale_view.xml',
         'views/asset_view.xml',
         'views/sale_view.xml',
         "views/sale_order_report_templates.xml",
         'views/account_view.xml',


        # Views Website
        # 'views/web_product_template.xml',

        # Menu

        # Reports
          'report/sale_report.xml',
          
        # Reports Configuration
    ],


    'assets': { 
        'web.report_assets_common': [
            '/static/src/js/boolean_fa_icon_widget.js',
            '/static/src/js/hide_details_translations.js',
            '/static/src/js/sale_layout_category_hide_detail.js',
            '/static/src/less/report.less',
        ],
    },
     
        
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
