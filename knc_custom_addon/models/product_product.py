# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import logging
import json
import re


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_lock = fields.Boolean(string="Locked", default=False, store=True, related="product_tmpl_id.is_lock")
    description = fields.Text(string="Description", compute="_compute_custom_description")  # Default Field
    default_code = fields.Char(copy=True)   # Default Field
    # Default code check flag
    is_similar_code = fields.Boolean(string="Similar DefaultCode", default=True)

    def _compute_attribute_related_description(self, record):
        description = ''
        attribute_set = {}

        for attr_value in record.product_template_variant_value_ids:
            # product_attribute_value_id (Product Attribute Value)
            # attribute_id (Product Attributes)
            attribute_set[attr_value.attribute_id.name] = attr_value.product_attribute_value_id.name

        for line in record.product_tmpl_id.attribute_line_ids:
            # attribute_id (Product Attributes)
            # value_ids (Product Attribute Value)
            if line.attribute_id.is_used_desc:
                # description += line.attribute_id.name + ' - '
                for value in line.value_ids:
                    if line.attribute_id.name in attribute_set:
                        if attribute_set[line.attribute_id.name] == value.name:
                            description += str(
                                line.attribute_id.prefix + ' ' if line.attribute_id.prefix else '') + value.name + str(
                                ' ' + line.attribute_id.suffix if line.attribute_id.suffix else '') + ', '
                    else:
                        description += str(
                            line.attribute_id.prefix + ' ' if line.attribute_id.prefix else '') + value.name + str(
                            ' ' + line.attribute_id.suffix if line.attribute_id.suffix else '') + ', '
        
        return description[:-2]
    
    def _compute_custom_description(self):
        for rec in self:
            rec.description = self._compute_attribute_related_description(record=rec)

    # Description for Sale, Quotation, others
    def _compute_ic_custom_description(self, product_id):
        description = ''

        if product_id.product_tmpl_id.default_code:
            description += '[' + product_id.product_tmpl_id.default_code + '] '
        if product_id.product_tmpl_id.product_brand_id:
            description += product_id.product_tmpl_id.product_brand_id.name + ' '
            description += product_id.product_tmpl_id.name + '\n'
        if product_id.product_tmpl_id.barcode:
            description += '[' + product_id.product_tmpl_id.barcode + '] '
        if product_id.product_tmpl_id.description_sale:
            description += product_id.product_tmpl_id.description_sale + '\n'
        description += product_id._compute_attribute_related_description(record=product_id)

        return description

    # Lock Button - Used for displaying information to user
    def button_lock(self):
        raise ValidationError('Please use the "Lock" button on the Product Template')

    # Unlock Button - Used for displaying information to user
    def button_unlock(self):
        raise ValidationError('Please use the "Unlock" button on the Product Template')

    # Modify product variants fields to read only on lock action
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # Fields for rejection as sample
        rejected_fields = [
            'image_1920', 'default_code', 'barcode', 'related_attributes_value_ids', 'lst_price', 'standard_price',
            'base_unit_count', 'base_unit_id', 'volume', 'weight', 'packaging_ids', 'product_variant_image_ids'
        ]

        res = super(ProductProduct, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field"):
                try:
                    if node.get("name") not in []:
                        modifiers = json.loads(node.get("modifiers"))
                        if 'readonly' not in modifiers:
                            modifiers['readonly'] = [['is_lock', '=', True]]
                        else:
                            if type(modifiers['readonly']) != bool:
                                modifiers['readonly'] = [['is_lock', '=', True]]
                        node.set('modifiers', json.dumps(modifiers))
                except:
                    pass
            res['arch'] = etree.tostring(doc)

        elif view_type == 'tree':
            for node in doc.xpath("//field"):
                try:
                    if node.get("name") not in []:
                        modifiers = json.loads(node.get("modifiers"))
                        if 'readonly' not in modifiers:
                            modifiers['readonly'] = [['is_lock', '=', True]]
                        else:
                            if type(modifiers['readonly']) != bool:
                                modifiers['readonly'] = [['is_lock', '=', True]]
                        node.set('modifiers', json.dumps(modifiers))
                except:
                    pass
            res['arch'] = etree.tostring(doc)
        return res

    ###############################################################################################################
    # ##################################  Related to Duplication of Default Code  #################################
    ###############################################################################################################

    def _check_update_default_codes(self, def_code):
        check_recs = self.env['product.product'].search([('default_code', '=', def_code)])
        if len(check_recs) > 1:
            for rec in check_recs:
                rec.write({'is_similar_code': True})
        elif len(check_recs) == 1:
            check_recs[0].write({'is_similar_code': False})
        else:
            self.write({'is_similar_code': False})

    def read(self, fields=None, load='_classic_read'):
        records = super(ProductProduct, self).read(fields=fields, load=load)
        similar_codes = []
        for idx, variant in enumerate(records):
            if 'default_code' in variant:
                if variant['default_code'] not in similar_codes:
                    self._check_update_default_codes(def_code=variant['default_code'])
                    similar_codes.append(variant['default_code'])
            records[idx] = variant

        return records

    def write(self, values):
        if "default_code" in values:
            self._check_update_default_codes(def_code=values['default_code'])
        return super(ProductProduct, self).write(values)

