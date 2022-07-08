# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api
from . import constants


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    is_related = fields.Boolean(string="Related Attribute", default=False, help="If enabled, you can assign the values of a related attribute to specific variants from the variants menu")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Temporary Store Attribute Values - Related Attributes
    def _compute_value_wt_lock(self):
        for db_variant in self.product_variant_ids:
            if db_variant and len(db_variant) > 0:
                if self.is_lock:
                    db_variant.store_variants_values(db_object=db_variant)
                    db_variant.message_post(
                        body=('● Product Variant has been <b>"Locked"</b>'), message_type='notification')
                else:
                    db_variant.restore_variants_values(db_object=db_variant)
                    db_variant.message_post(
                        body=('● Product Variant has been <b>"Unlocked"</b>'), message_type='notification')


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Additional Sync & Restore fields
    is_sync_value = fields.Boolean(string="Is Sync?", default=False)
    related_attributes_value_ids = fields.Many2many(
        "product.template.attribute.value", "product_related_attributes_value_rel",
        string="Related Attribute Values")
    restore_attribute_value_ids = fields.Many2many(
        "product.template.attribute.value", "restore_product_related_attributes_value_rel",
        string="Restore Values", store=True)
    tmp_related_attributes_value_ids = fields.Many2many(
        "product.template.attribute.value", "tmp_product_related_attributes_value_rel",
        string="Temporary Values", store=True)

    '''
    # Remove existing functionality
    
    @api.onchange('related_attributes_value_ids')
    def _compute_manipulate_related_values(self):
        if len(self.tmp_related_attributes_value_ids) == 0:
            self.tmp_related_attributes_value_ids = self.product_template_variant_value_ids

        if self.related_attributes_value_ids:
            self.product_template_variant_value_ids = self.tmp_related_attributes_value_ids + self.related_attributes_value_ids
        else:
            self.product_template_variant_value_ids = self.tmp_related_attributes_value_ids
    '''

    @api.onchange('is_sync_value')
    def _compute_related_oc_values(self):
        # Enable the Product Template Lock
        cr_product_tmpl_id = self.env["product.template"].search([('name', '=', self.product_tmpl_id.name)])
        if cr_product_tmpl_id and len(cr_product_tmpl_id) > 0:
            if not cr_product_tmpl_id[0].is_lock:
                cr_product_tmpl_id[0].write({"is_lock": True})

        if self.is_sync_value:
            self.restore_attribute_value_ids = self.product_template_variant_value_ids
            if len(self.tmp_related_attributes_value_ids) == 0:
                self.tmp_related_attributes_value_ids = self.product_template_variant_value_ids

            if self.related_attributes_value_ids:
                self.product_template_variant_value_ids = self.tmp_related_attributes_value_ids + self.related_attributes_value_ids
            else:
                self.product_template_variant_value_ids = self.tmp_related_attributes_value_ids
        else:
            db_variants = self.env["product.product"].search([
                '&', ('product_tmpl_id', '=', cr_product_tmpl_id[0].id), ('is_sync_value', '=', True)])
            if len(db_variants) < 2:
                cr_product_tmpl_id[0].write({"is_lock": False})
            self.product_template_variant_value_ids = self.restore_attribute_value_ids

    def restore_variants_values(self, db_object):
        db_object.write({
            'is_sync_value': False,
            'product_template_variant_value_ids': db_object.restore_attribute_value_ids
        })
        # self.product_template_variant_value_ids = self.restore_attribute_value_ids

    def store_variants_values(self, db_object):
        if len(db_object.restore_attribute_value_ids) > 0:
            records = db_object.restore_attribute_value_ids + db_object.related_attributes_value_ids
        else:
            records = db_object.product_template_variant_value_ids + db_object.related_attributes_value_ids
            db_object.write({
                'restore_attribute_value_ids': db_object.product_template_variant_value_ids
            })

        db_object.write({
            'is_sync_value': True,
            'product_template_variant_value_ids': records
        })
        #self.product_template_variant_value_ids = self.restore_attribute_value_ids + self.related_attributes_value_ids

    def _compute_related_value_ids(self):
        tmp_related_value_ids = []

        for attribute in self.env["product.attribute"].search([('is_related', '=', True)]):
            tmp_related_value_ids += [value.id for value in attribute.value_ids]

        #########################################################################################################
        # ##########################       Collect Product Template Attribute Ids      ##########################
        #########################################################################################################

        if self.product_tmpl_id.attribute_line_ids and len(self.product_tmpl_id.attribute_line_ids) > 0:
            for attr_line in self.product_tmpl_id.attribute_line_ids:
                if attr_line.value_ids and len(attr_line.value_ids) > 0:
                    for attr_value in attr_line.value_ids:
                        chk_exist_value = self.env[constants.PRODUCT_ATTRIBUTE_VALUE_MODEL].search([
                            ('name', '=', attr_value.name)
                        ])
                        if chk_exist_value[0].id not in tmp_related_value_ids:
                            tmp_related_value_ids.append(chk_exist_value[0].id)

        return [("id", "in", tmp_related_value_ids)]
