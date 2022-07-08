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
        'base', 'contacts', 'base_address_city', 'base_location', 'partner_multi_relation',
        'stock', 'website', 'website_sale', 'website_sale_comparison', 'crm', 'project',
        'sale', 'account', 'board'
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
        'views/project.xml',
        # 'views/opportunity.xml',
        'views/competitor.xml',
        'views/product_brand.xml',
        'views/product_state.xml',
        'views/product_product.xml',
        'views/product_template.xml',
        'views/product_attribute.xml',
        'views/product_attribute_related.xml',
        'views/product_attribute_set.xml',
        'views/product_attribute_tag.xml',
        'views/sale_order.xml',
        'views/waybill.xml',
        'views/product_product_code.xml',
        'views/account_bill_views.xml',
        # 'views/x_product_attribute_value_supplier.xml',

        # Views Website
        # 'views/web_product_template.xml',

        # Menu
        'views/_menu.xml',
        'views/_menu_views.xml',

        # Reports
        'report/product_datasheet_report.xml',
        'report/template_datasheet_report.xml',
        'report/waybill_report.xml',

        # Reports Configuration
        'report/_report_layout.xml',
        'data/report_paperformat_data.xml',
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
