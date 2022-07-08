# Code Checked & Confirmed by Panos on ../../2022
from odoo import fields, models, api
import logging


# Product Datasheet Report
class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    # @api.depends('attribute_id')
    # def _get_category(self):
    #     for rec in self:
    #         rec.category_id = rec.attribute_id.category_id.id

    category_id = fields.Many2one(
        "product.attribute.category", string="Attribute Category", related='attribute_id.category_id', store=True)


# Product Datasheet Report
class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_features(self):
        for rec in self:
            template_attributes = rec.product_tmpl_id.attribute_line_ids.mapped('attribute_id')
            product_attribute_line = self.env['product.template.attribute.line']
            groupby = 'category_id'
            attribute_group = product_attribute_line.read_group([
                ('attribute_id', 'in', template_attributes.ids)], fields=[groupby], groupby=[groupby])
            result = []
            for group in attribute_group:
                category = ''
                attribute_data = {}
                domain = [
                    ('attribute_id', 'in', template_attributes.ids), ('product_tmpl_id', '=', rec.product_tmpl_id.id)]

                if group[groupby]:
                    domain += [(groupby, '=', int(group[groupby][0]))]
                    category = self.env['product.attribute.category'].search([('id', '=', int(group[groupby][0]))],
                                                                             limit=1).name
                attribute_data['lines'] = []
                attribute_data['category'] = ''

                # Custom code for related attribute value ids
                attribute_data['related'] = rec.related_attributes_value_ids

                # Print All Attributes & All Values set on Product Template
                for line in product_attribute_line.search(domain):
                    attribute_data['lines'].append(line)
                    attribute_data['category'] = category
                # Custom Logic - 15/06/2022
                if attribute_data['category']:
                    result.append(attribute_data)

                # Print only Attributes & Values which are set to Create Variants
                # attribute_lines = product_attribute_line.search(domain)
                # for line in attribute_lines:
                #     if line.attribute_id.create_variant == 'no_variant':
                #         attribute_data['lines'].append(line)
                #         attribute_data['category'] = category
                # result.append(attribute_data)

        return result
