# Code Checked & Confirmed by Panos on ../../2022
import logging

from odoo import models, fields, api
from datetime import *
from lxml import etree
import json


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_lock = fields.Boolean(string="Locked", default=False, store=True)
    version = fields.Char(string="Version", tracking=True)
    creation_days = fields.Integer(string="Creation Days", compute="_compute_create_no_days")

    # Duplicate Template & Adjust Default Code by adding *
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        rec = super(ProductTemplate, self).copy(default)
        rec.write({'is_lock': False})
        # for prev_variant, copy_variant in zip(self.product_variant_ids, rec.product_variant_ids):
        #     if prev_variant.default_code:
        #         copy_def_code = '*' + prev_variant.default_code
        #         copy_variant.write({'default_code': copy_def_code})
        # Copy Wizard Information
        chk_wizard_id = self.env["product.code.generator.wizard"].search([('product_tmpl_id', '=', self.id)])
        if len(chk_wizard_id) > 0:
            self.env["product.code.generator.wizard"].create({
                "product_tmpl_id": rec.id,
                "product_tmpl_code": chk_wizard_id[0].product_tmpl_code,
                "product_syntax_id": chk_wizard_id[0].product_syntax_id.id,
                "product_brand_id": chk_wizard_id[0].product_brand_id.id,
                "version_ids": [x.id for x in chk_wizard_id[0].version_ids],
                "version_value_ids": [x.id for x in chk_wizard_id[0].version_value_ids]
            })
        return rec

    # Calculate datetime difference in days for use with invisible attribute
    def _compute_create_no_days(self):
        for rec in self:
            datetime_diff = datetime.now() - self.create_date
            rec.creation_days = datetime_diff.days

    # Lock Button - Post message to chatter, assign related attribute values to variants
    def button_lock(self):
        for rec in self:
            self.message_post(
                body=('● Product Template & Variants has been <b>"Locked"</b>'), message_type='notification')
            rec.is_lock = True
            rec._compute_value_wt_lock()

    # Unlock Button - Post message to chatter, assign related attribute values to variants
    def button_unlock(self):
        for rec in self:
            self.message_post(
                body=('● Product Template & Variants has been <b>"Unlocked"</b>'), message_type='notification')
            rec.is_lock = False
            rec._compute_value_wt_lock()

    # Modify product template fields to read only on lock action
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ProductTemplate, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field"):
                if node.get('name') not in ['priority']: # List of fields that not effect using lock option
                    try:
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


class eCommerceCategories(models.Model):
    _inherit = 'product.public.category'

    def name_get(self):
        result = []
        for categ in self:
            result.append((categ.id, categ.name))
        return result
