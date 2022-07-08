# Code Checked & Confirmed by Panos on ../../2022
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


# Based on OCA Module product_state - https://github.com/OCA/product-attribute/tree/15.0/product_state
class ProductStates(models.Model):
    _name = "product.states"
    _description = "Product States"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(comodel_name="State Name", required=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string="Comments / Notes")
    product_ids = fields.One2many("product.template", "product_state_id", string="State Products",)
    products_count = fields.Integer(string="Number of Products", compute="_compute_products_count",)
    default = fields.Boolean(string="Default state")

    @api.depends("product_ids")
    def _compute_products_count(self):
        data = self.env["product.template"].read_group(
            [("product_state_id", "in", self.ids)],
            ["product_state_id"],
            ["product_state_id"],
        )
        mapped_data = {
            record["product_state_id"][0]: record["product_state_id_count"]
            for record in data
        }
        for state in self:
            state.products_count = mapped_data.get(state.id, 0)

    @api.constrains("default")
    def _check_default(self):
        if self.search_count([("default", "=", True)]) > 1:
            raise ValidationError(_("There should be only one default state"))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # product_state_id = fields.Many2one("product.states", string="State", group_expand="_read_group_state_id", inverse="_inverse_product_state_id", default=lambda self: self._get_default_product_state().id, index=True, tracking=True)

    state = fields.Char(
        string="Product Status", index=True, compute="_compute_product_state",
        inverse="_inverse_product_state", readonly=True, store=True,
    )
    product_state_id = fields.Many2one("product.states", string="State", group_expand="_read_group_state_id",
                                       inverse="_inverse_product_state_id",
                                       index=True,
                                       tracking=True)

    def _inverse_product_state_id(self):
        """
        Allow to ease triggering other stuff when product state changes
        without a write()
        """

    @api.model
    def _get_default_product_state(self):
        return self.env["product.states"].search([("default", "=", True)], limit=1)

    @api.depends("product_state_id")
    def _compute_product_state(self):
        for product_tmpl in self:
            try:
                product_tmpl.state = product_tmpl.product_state_id.code
            except:
                product_tmpl.state = None

    def _inverse_product_state(self):
        for product_tmpl in self:
            self._set_product_state_id(product_tmpl)

    @api.model
    def _read_group_state_id(self, states, domain, order):
        return states.search([])
