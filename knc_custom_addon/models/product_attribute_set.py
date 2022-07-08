# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging


class ProductAttributeSet(models.Model):
    _name = "product.attribute.set"
    _description = "Product Attribute Sets"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Product Template Attribute Set Name", required=True)
    attribute_line_ids = fields.One2many("product.attribute.set.line", "attribute_set_id", copy=True, string="Related Attributes")


class ProductAttributeSetLine(models.Model):
    _name = "product.attribute.set.line"
    _description = "Product Attribute Sets Lines"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", related="attribute_id.sequence")
    attribute_set_id = fields.Many2one("product.attribute.set", string="Attribute Set")
    attribute_id = fields.Many2one(
        "product.attribute", string="Attribute", ondelete="restrict", required=True, index=True)
    value_ids = fields.Many2many(
        "product.attribute.value", string="Attribute Values", domain="[('attribute_id', '=', attribute_id)]",
        relation="product_attribute_value_product_attribute_set_line_rel", ondelete="restrict")
    value_count = fields.Integer(compute="_compute_value_count", store=True, readonly=True)

    def get_value_ids_length(self, record):
        return len(record.value_ids)

    @api.depends('value_ids')
    def _compute_value_count(self):
        for record in self:
            record.value_count = self.get_value_ids_length(record)

    @api.depends('value_ids')
    def _compute_tmp_value_count(self):
        for record in self:
            record.tmp_value_count = self.get_value_ids_length(record)

    @api.onchange('value_ids')
    def _compute_value_by_change(self):
        for record in self:
            record.value_count = self.get_value_ids_length(record)

    @api.onchange('attribute_id')
    def _onchange_attribute_id(self):
        self.value_ids = self.value_ids.filtered(lambda pav: pav.attribute_id == self.attribute_id)

    # def create(self, values):
    #     for rec in values:
    #         if len(rec['value_ids'][0][2]) == 0:
    #             raise ValidationError("Please select atleast one attribute value")
    #     return super(ProductAttributeSetLine, self).create(values)
    #
    # def write(self, values):
    #     if type(values) == list:
    #         for rec in values:
    #             if 'value_ids' in rec and len(rec['value_ids'][0][2]) == 0:
    #                 raise ValidationError("Please select atleast one attribute value")
    #     else:
    #         if 'value_ids' in values and len(values['value_ids'][0][2]) == 0:
    #             raise ValidationError("Please select atleast one attribute value")
    #     return super(ProductAttributeSetLine, self).write(values)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attribute_set_id = fields.Many2one('product.attribute.set', string="Related Attribute Set")

    def show_confirmation_popup(self):
        if self.attribute_set_id:
            rec = self.env['product.attribute.set.wizard'].search([('product_tmpl_id', '=', self.id)])
            if rec and len(rec) > 0:
                rec = rec[0]
            else:
                rec = self.env['product.attribute.set.wizard'].create({'product_tmpl_id': self.id})
            return {
                'name': _("Confirmation?"),
                'type': 'ir.actions.act_window',
                'res_model': 'product.attribute.set.wizard',
                'res_id': rec.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
            }

    def execute_collect_value(self, product_tmpl_id):
        if product_tmpl_id.attribute_set_id:
            self.env["product.template.attribute.line"].search([('product_tmpl_id', '=', product_tmpl_id.id)]).unlink()

            for attr_line in product_tmpl_id.attribute_set_id.attribute_line_ids:
                chk_rec = self.env["product.template.attribute.line"].search([
                    '&', ('product_tmpl_id', '=', product_tmpl_id.id), ('attribute_id', '=', attr_line.attribute_id.id)
                ])
                if chk_rec and len(chk_rec) > 0:
                    chk_rec[0].write({
                        'value_ids': [(6, 0, [x.id for x in attr_line.value_ids])]
                    })
                else:
                    self.env["product.template.attribute.line"].create({
                        'product_tmpl_id': product_tmpl_id.id,
                        'attribute_id': attr_line.attribute_id.id,
                        'value_ids': [(6, 0, [x.id for x in attr_line.value_ids])]
                    })


# Wizard for confirmation
class ConfirmWizard(models.TransientModel):
    _name = 'product.attribute.set.wizard'

    yes_no = fields.Char(default='Do you want to proceed?')
    product_tmpl_id = fields.Many2one('product.template', string="Related Product")

    def yes(self):
        self.env['product.template'].execute_collect_value(self.product_tmpl_id)
        return True

    def no(self):
        return False
