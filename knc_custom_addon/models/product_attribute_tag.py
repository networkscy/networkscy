from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging


class ProductAttributeTag(models.Model):
    _name = "product.attribute.tag"
    _description = "Product Attribute Tags"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Attribute Tag Name", required=True)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    attribute_tags_ids = fields.Many2many("product.attribute.tag", "product_attribute_tag_rel", "attribute_tags_ids",
                                          "attribute_id", string="Attribute Tags")
