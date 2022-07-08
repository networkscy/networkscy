# from odoo import models, fields, api
#
#
# class AttributeValueSupplierComb(models.Model):
#     _name = 'product.code.generator.brand'
#
#     name = fields.Char(string='Characters', required=True)
#     brand_id = fields.Many2one('product.brands', string='Brand', required=True)
#     attr_value_id = fields.Many2one('product.attribute.value', string="Attribute Value")
#
#
# class AttributeValue(models.Model):
#     _inherit = 'product.attribute.value'
#
#     brand_attr_comb_ids = fields.One2many(
#         'product.code.generator.brand', 'attr_value_id', string="Supplier Attribute Combs")
#
#
# class ProductBrand(models.Model):
#     _inherit = 'product.brands'
#
#     attr_brand_comb_ids = fields.One2many(
#         'product.code.generator.brand', 'brand_id', string="Attribute Supplier Combs")
