# Code Checked & Confirmed by Panos on ../../2022
from odoo import api, fields, models


# Based on OCA Module product_brand - https://github.com/OCA/brand/commits/15.0/product_brand
class ProductBrands(models.Model):
    _name = "product.brands"
    _description = "Product Brands"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char("Brand Name", required=True)
    active = fields.Boolean(default=True)
    logo = fields.Binary(string="Brand Logo")
    origin = fields.Many2one("res.country", string="Brand Origin")
    website = fields.Char(string="Brand Website")
    partner_id = fields.Many2one("res.partner", string="Related Partner", domain="[('is_company', '=', True)]", ondelete="restrict")
    notes = fields.Char(string="Comments / Notes")
    related_products_ids = fields.One2many("product.template", "product_brand_id", string="Brand Products")
    products_count = fields.Integer(string="Number of Products", compute="_compute_products_count")

    @api.depends("related_products_ids")
    def _compute_products_count(self):
        product_model = self.env["product.template"]
        groups = product_model.read_group(
            [("product_brand_id", "in", self.ids)],
            ["product_brand_id"],
            ["product_brand_id"],
            lazy=False,
        )
        data = {group["product_brand_id"][0]: group["__count"] for group in groups}
        for brand in self:
            brand.products_count = data.get(brand.id, 0)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_brand_id = fields.Many2one("product.brands", string="Product Brand", tracking=True)
