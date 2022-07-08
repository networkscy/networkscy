# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging


class ProductCodeSyntax(models.Model):
    _name = "product.code.syntax"
    _description = "Product Code Syntax"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Selection([
        ('default_code', 'Product Template Code'),
        ('seperator', 'Custom Seperator'),
        ('attribute', 'Related Attribute')],
        string="Selection", required=True)
    value = fields.Char(string="Related Value")
    value_sel = fields.Many2one("product.attribute", string="Related Attribute")


class ProductCodeSyntaxSet(models.Model):
    _name = "product.code.syntax.set"
    _description = "Product Code Syntax Sets"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Product Code Syntax Set Name", required=True)
    product_code_def_ids = fields.Many2many("product.code.syntax", "product_code_default_ids", string="Related Values")
    # product_code_def_ids = fields.Many2many('product.code.syntax', 'product_code_default_rel', 'pcs_id', 'pcd_id', string="Product Code Lines")


class ProductCodeGenerator(models.TransientModel):
    _name = "product.code.generator"
    _description = "Product Code Generator"
    _inherit = "product.code.syntax"

    product_wiz_id = fields.Many2one("product.code.generator.wizard", string="Product Code Wizard ID")
    value_tmpl_code = fields.Char(related="product_wiz_id.product_tmpl_code", string="Template Code", readonly=True)

    # @api.onchange('name')
    # def _calculate_values(self):
    #     if self.name:
    #         if self.name == 'attribute':
    #             filter_vals = [line_id.attribute_id.id for line_id in self.product_wiz_id.product_tmpl_id.attribute_line_ids if line_id.attribute_id.create_variant == 'always']
    #             tmp_vals = self.env['product.code.generator.wizard'].search([('product_tmpl_id', '=', self.product_wiz_id.product_tmpl_id.id)])
    #             if len(tmp_vals) > 0:
    #                 tmp_vals = [version_id.value_sel.id for version_id in tmp_vals[0].version_ids]
    #                 filter_vals = list(set(filter_vals) - set(tmp_vals))
    #             return {
    #                 'domain': {
    #                     'value_sel': [('id', 'in', filter_vals)]
    #                 }
    #             }


class ProductCodeGeneratorValues(models.TransientModel):
    _name = "product.code.generator.value"
    _description = "Product Code Generator Values"

    name = fields.Char(string="Attribute Value", required=True, readonly=True)
    attribute_id = fields.Many2one('product.attribute', string="Attribute Name", readonly=True)
    value = fields.Char(string="Brand Character")
    product_tmpl_id = fields.Many2one("product.template", string="Product Template", readonly=True)
    product_version_id = fields.Many2one("product.code.generator.wizard", string="Reference")

    @api.onchange('value')
    def _complute_auto_save_value(self):
        if self.product_version_id.product_brand_id:
            for attr_line in self.product_version_id.product_brand_id.attr_brand_comb_ids:
                if self.name == attr_line.attr_value_id.name:
                    attr_line.write({'name': self.value})
                    break


        # Additional Warning Message
        # else:
        #     raise ValidationError("Please select product brand first to update value")


class ProductCodeGeneratorWizard(models.TransientModel):
    _name = "product.code.generator.wizard"
    _description = "Product Code Generator Wizard"

    product_tmpl_id = fields.Many2one("product.template", string="Product Template", readonly=True)
    product_tmpl_code = fields.Char(related="product_tmpl_id.default_code", string="Internal Reference", readonly=False)

    product_syntax_id = fields.Many2one("product.code.syntax.set", string="Code Syntax Set")
    product_brand_id = fields.Many2one(related="product_tmpl_id.product_brand_id", string="Related Brand", readonly=False)
    version_ids = fields.One2many("product.code.generator", "product_wiz_id", string="Sequence Versions")
    version_value_ids = fields.One2many("product.code.generator.value", "product_version_id", string="Version Values")

    @api.onchange('product_syntax_id')
    def _compute_syntax_set(self):
        if self.product_syntax_id:
            self.write({'version_ids': [], 'version_value_ids': []})
            version_ids = []
            for line in self.product_syntax_id.product_code_def_ids:
                data_params = {
                    'product_wiz_id': self.id,
                    'name': line.name
                }
                if line.name == 'default_code':
                    data_params['value'] = self.product_tmpl_code
                elif line.name == 'seperator':
                    data_params['value'] = line.value
                else:
                    data_params['value_sel'] = line.value_sel.id
                version_ids.append(self.env['product.code.generator'].create(data_params).id)

            if len(version_ids) > 0:
                self.write({'version_ids': version_ids, 'version_value_ids': []})
                self.generate_versions()

        self.ensure_one()
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.code.generator.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('product_tmpl_code')
    def _compute_template_code(self):
        if self.product_tmpl_code:
            if self.product_tmpl_code != self.product_tmpl_id.default_code:
                self.product_tmpl_id.write({'default_code': self.product_tmpl_code})

    @api.onchange('product_brand_id')
    def _complute_autoload_values(self):
        if self.product_brand_id:
            self.product_tmpl_id.write({'product_brand_id': self.product_brand_id.id})
            for line_value in self.version_value_ids:
                for attr_line in self.product_brand_id.attr_brand_comb_ids:
                    if line_value.name == attr_line.attr_value_id.name:
                        line_value.write({'value': attr_line.name})
                        break
        else:
            self.product_tmpl_id.write({'product_brand_id': False})

    def create_update_product_code_values(self):
        if self.product_brand_id:
            for ver_line in self.version_value_ids:
                db_attr_value_id = self.env['product.attribute.value'].search([('name', '=', ver_line.name)])
                if len(db_attr_value_id) > 0:
                    chk_exist_rec = self.env['product.code.generator.brand'].search([
                        '&', ('brand_id', '=', self.product_brand_id.id), ('attr_value_id', '=', db_attr_value_id[0].id)
                    ])
                    if len(chk_exist_rec) > 0:
                        chk_exist_rec.write({'name': ver_line.value})
                    else:
                        self.env['product.code.generator.brand'].create({
                            'name': ver_line.value,
                            'brand_id': self.product_brand_id.id,
                            'attr_value_id': db_attr_value_id[0].id
                        })

    def yes(self):
        if not self.product_brand_id:
            raise ValidationError("Please select Brand to proceed first")
        # Create Update Product Code Value
        self.create_update_product_code_values()

        for variant in self.product_tmpl_id.product_variant_ids:
            gen_code, seperator, is_seperator_last, done_values, is_empty_value = "", "", False, [], False
            separator_lists = []
            for idx, version_id in enumerate(self.version_ids):
                if version_id.name == "default_code" or version_id.name == "seperator":
                    if version_id.name == "default_code" and not version_id.value_tmpl_code:
                        raise ValidationError("Please fill product template code first to proceed further")

                    if version_id.name == "seperator":
                        if version_id.value:
                            separator_lists.append(version_id.value)
                            seperator = version_id.value
                        else:
                            separator_lists.append(' ')
                            seperator = ' '
                        is_seperator_last = True

                    if version_id.value and not is_empty_value:
                        gen_code += version_id.value
                    elif version_id.name == "default_code":
                        gen_code += self.product_tmpl_code
                    else:
                        gen_code += ' '

                else:
                    is_inst_flag = False
                    for value_id in self.version_value_ids:
                        for variant_attr_value in variant.product_template_attribute_value_ids:
                            if value_id.name not in done_values and value_id.name == variant_attr_value.product_attribute_value_id.name:
                                if value_id.value:
                                    gen_code += value_id.value
                                    is_empty_value = False
                                else:
                                    is_empty_value = True

                                done_values.append(value_id.name)
                                is_inst_flag = True
                                break

                        if is_inst_flag:
                            break
                        else:
                            ValidationError("Please Adjust Attribute correctly")

                    is_seperator_last = False

            if seperator and seperator == gen_code[-1] and not is_seperator_last:
                gen_code = gen_code[:-1]

            ###############################################################################
            # ##################      Extra Filtration for Separator      #################
            ###############################################################################

            if gen_code[-1] in separator_lists:
                gen_code = gen_code[:-1]

            prev_idx = 0
            for spl in separator_lists:
                if spl and spl in gen_code:
                    spl_idx = gen_code.index(spl)
                    if (prev_idx + 1) == spl_idx:
                        gen_code = gen_code[0:spl_idx] + gen_code[(spl_idx + 1):]
                    prev_idx = spl_idx

            variant.write({"default_code": gen_code.strip()})

        if self.product_tmpl_code:
            self.product_tmpl_id.write({'default_code': self.product_tmpl_code})
        return True

    def no(self):
        return False

    def generate_versions(self):
        if not self.product_brand_id:
            raise ValidationError("Please select product brand first to proceed further")

        version_value_ids = []
        for version_id in self.version_ids:
            if version_id.name == "attribute":
                if len(version_id.value_sel) > 0:
                    selective_attr = [
                        line_id for line_id in self.product_tmpl_id.attribute_line_ids if line_id.attribute_id.id == version_id.value_sel.id
                    ]
                    if len(selective_attr) > 0:
                        for attr_value_id in selective_attr[0].value_ids:
                            rec_params = {
                                'name': attr_value_id.dis_name,
                                'attribute_id': version_id.value_sel.id,
                                'product_version_id': self.id,
                                'product_tmpl_id': self.product_tmpl_id.id
                            }

                            if self.product_brand_id:
                                for line_id in attr_value_id.brand_attr_comb_ids:
                                    if line_id.brand_id.name == self.product_brand_id.name:
                                        rec_params['value'] = line_id.name

                            version_value_ids.append(self.env['product.code.generator.value'].create(rec_params).id)
                    else:
                        raise ValidationError('Please select correct attributes')
                else:
                    raise ValidationError('Please select correct attributes')

        if len(version_value_ids) > 0:
            self.write({'version_value_ids': version_value_ids})

        self.ensure_one()
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.code.generator.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def remove_versions(self):
        self.write({'version_value_ids': []})
        self.env['product.code.generator.value'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)]).unlink()
        self.ensure_one()
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.code.generator.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class ProductCodeGeneratorBrand(models.Model):
    _name = "product.code.generator.brand"
    _description = "Product Code Generator Brands"

    name = fields.Char(string="Brand Character", required=False)
    brand_id = fields.Many2one("product.brands", string="Related Brand", required=True)
    attr_value_id = fields.Many2one("product.attribute.value", string="Related Attribute Value")


class ProductCodeGeneratorBrandValues(models.Model):
    _inherit = "product.attribute.value"

    brand_attr_comb_ids = fields.One2many(
        "product.code.generator.brand", "attr_value_id", string="Related Brand Code Characters")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def update_default_code(self):
        # Condition for Default code of Product template
        # if self.product_tmpl_id.default_code:
        rec = self.env['product.code.generator.wizard'].search([
            ('product_tmpl_id', '=', self.product_tmpl_id.id)
        ])
        if len(rec) == 0:
            rec = self.env['product.code.generator.wizard'].create({'product_tmpl_id': self.product_tmpl_id.id})
        return {
            'name': _("Generate Internal References for Product Variants"),
            'type': 'ir.actions.act_window',
            'res_model': 'product.code.generator.wizard',
            'res_id': rec[0].id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }


class ProductBrand(models.Model):
    _inherit = "product.brands"

    attr_brand_comb_ids = fields.One2many(
        "product.code.generator.brand", "brand_id", string="Related Attribute Value Characters")
