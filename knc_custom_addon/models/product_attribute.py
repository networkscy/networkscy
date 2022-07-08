# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    name_alt = fields.Char(string="Short Name")
    note = fields.Char(string="Note")
    prefix = fields.Char(string="Prefix (Before)")
    suffix = fields.Char(string="Suffix (After)")
    is_float = fields.Boolean(string="Contain Float Values", default=False)
    is_integer = fields.Boolean(string="Contain Integer Values", default=False)
    is_used_desc = fields.Boolean(string="Used in Description", default=False)
    is_single_value = fields.Boolean(string="Single Value Selection", default=False)
    comments = fields.Char(string="Comments")

    # ok
    # Action for Generating Attribute Display Name & Adjusting the Sequence of Values
    def update_attr_values(self, sorted_value_ids):
        idx = 1
        for attr_val in sorted_value_ids:
            update_dis_name = ''
            if self.prefix:
                update_dis_name += str(self.prefix) + ' '
            update_dis_name += attr_val.name
            if self.suffix:
                update_dis_name += ' ' + str(self.suffix)
            attr_val.write({
                'dis_name': update_dis_name,
                'sequence': idx
            })
            idx += 1

    # ok
    # Generate Attribute Value Display Name with Prefix & Suffix & Adjust the Sequence of Values
    def write(self, values):
        save_rec = super(ProductAttribute, self).write(values)
        try:
            update_rec = self.env['product.attribute'].search([('id', '=', self.id)])
            if self.is_float:
                # When is_float is enabled, then sort values by name_float field
                self.update_attr_values(update_rec.value_ids.sorted(key=lambda r: r.name_float))
            elif self.is_integer:
                # When is_integer is enabled, then sort values by name_integer field
                self.update_attr_values(update_rec.value_ids.sorted(key=lambda r: r.name_integer))
            else:
                # When is_integer or is_float not enabled, then sort values by sequence field
                self.update_attr_values(update_rec.value_ids)
        except:
            pass
        return save_rec

    # checking
    # Convert Existing Values to Float Format, Copy Attribute Value to Float Field & Generate Value Printed Name
    @api.onchange('is_float')
    def _compute_float_value_ids(self):
        for line_value in self.value_ids:
            try:
                if self.is_float:
                    tmp_value = str(line_value.name)
                    line_value.name_float = float(tmp_value)

                    # tmp_value = str(line_value.name).replace(',', '')
                    # line_value.name_float = float(tmp_value)
                    # tmp_fraction = str(line_value.name_float).split('.')

                    # 1 Decimal / Fraction Point / 0.0
                    # if len(tmp_fraction) == 0:
                    #     upd_value = tmp_fraction[0] + '.0'
                    # elif len(tmp_fraction) == 1:
                    #     upd_value = str(line_value.name_float)
                    # else:
                    #     upd_value = str(tmp_fraction[0] + '.' + tmp_fraction[1][0])
                    # line_value.name = "{:,}".format(float(upd_value))

                    # 2 Decimals / Fraction Points / 0.00
                    # if len(tmp_fraction[1]) == 2:
                    #     line_value.name = "{:,}".format(line_value.name_float)
                    # else:
                    #     line_value.name = "{:,}".format(line_value.name_float) + '0'

                else:
                    line_value.name_float = None
            except Exception as ex:
                raise ValidationError("Warning! Some Values could not be converted to Float type."
                                      "Please check the values to contain only numbers and try again > " + str(ex))

    # checking
    # Convert Existing Values to Integer Format, Copy Attribute Value to Integer Field & Generate Value Printed Name
    @api.onchange('is_integer')
    def _compute_integer_value_ids(self):
        for line_value in self.value_ids:
            try:
                if self.is_integer:
                    tmp_value = str(line_value.name)
                    line_value.name_integer = int(tmp_value)

                    # tmp_value = line_value.name.replace(',', '')
                    # Fraction part for float number
                    # fraction = tmp_value.split('.')[1] if '.' in tmp_value else None

                    # line_value.name_integer = int(tmp_value.split('.')[0])
                    # tmp_fraction = str(line_value.name_integer)
                    # if len(tmp_fraction) >= 4:
                    #     line_value.name = "{:,}".format(line_value.name_integer)
                    # else:
                    #     line_value.name = "{0}".format(line_value.name_integer)

                else:
                    line_value.name_integer = None
            except Exception as ex:
                raise ValidationError("Warning! Some Values could not be converted to Integer type."
                                      "Please check the values to contain only numbers and try again > " + str(ex))


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    name = fields.Char(string="Name Value")  # Default Field
    dis_name = fields.Char(string="Printed Name", related="name")
    name_float = fields.Float(string="Float Value", store=True)
    name_integer = fields.Integer(string="Integer Value", store=True)
    is_custom = fields.Boolean(string="is Custom Value")  # Default Field
    is_child_float = fields.Boolean(string="is Float Value", related="attribute_id.is_float")
    is_child_integer = fields.Boolean(string="is Integer Value", related="attribute_id.is_integer")

    # Convert Name to Integer or Float Value
    @api.model
    def create(self, values):
        rec = super(ProductAttributeValue, self).create(values)
        if rec.is_child_integer:
            rec.write({'name_integer': int(rec.name)})
        elif rec.is_child_float:
            rec.write({'name_float': float(rec.name)})
        return rec

    def write(self, values):
        if 'name' in values:
            if self.is_child_integer and 'name_integer' not in values:
                values['name_integer'] = int(values['name'])
            elif self.is_child_float and 'name_float' not in values:
                values['name_float'] = float(values['name'])
        return super(ProductAttributeValue, self).write(values)

    # ok
    # Validate that the Attribute Value is Float Type during Creation
    def check_float_validation(self, value):
        if bool(re.search(r"^[\d]+$|^\d{1,4}\.[1-9]{1}$|^\d{1,4}\.[\d][1-9]{1}$", value)):
            return True
        raise ValidationError("Warning! The attribute value must contain only numbers of Integer or Float type \n"
                              "Not Acceptable values are in the format of 15.0 or 15.00 or 15.50 or 15,0 \n"
                              "Acceptable values are in the format of 15 or 15.5 or 15.05")

        # 1 Decimal / Fraction Point / 0.0
        # if bool(re.search(r"^\d{1,3}\.\d{1}$|^\d{1,3}\,\d{3}\.\d{1}$", value)):
        #     return True
        # raise ValidationError("Warning! The Value must be Float type in the format of 0.0 or 0,000.0")

        # 2 Decimals / Fraction Points / 0.00
        # if bool(re.search(r"^\d{1,3}\.\d{2}$|^\d{1,3}\,\d{3}\.\d{2}$", value)):
        #     return True
        # raise ValidationError("Warning! The Value must be Float type in the format of 0.00 or 0,000.00")

    # ok
    # Validate that the Attribute Value is Integer Type during Creation
    def check_integer_validation(self, value):
        if bool(re.search(r"^[\d]+$", value)):
            return True
        raise ValidationError("Warning! The attribute value must contain only numbers of Integer type \n"
                              "Not Acceptable values are in the format of 10.5 or 100.5 or 150,5 \n"
                              "Acceptable values are in the format of 5 or 50 or 100")

        # if bool(re.search(r"^\d{1,3}$|^\d{1,3}\,\d{3}$|^\d{1,3}\,\d{3}\,\d{3}$", value)):
        #     return True
        # raise ValidationError("Warning! The attribute value must be Integer type in the format of 0 or 0,000 or 0,000,000")

    # checking
    # Validate Attribute Value Name as per Float & Integer Value Format
    @api.constrains('name')
    def _check_value(self):
        for rec in self:
            if rec.attribute_id.is_float:
                if rec.check_float_validation(value=rec.name):
                    # self.name_float = self.name.replace(',', '')
                    return True
            elif rec.attribute_id.is_integer:
                if rec.check_integer_validation(value=rec.name):
                    # self.name_integer = self.name.replace(',', '')
                    return True

    # checking
    # Validate Attribute Value Name as per Float & Integer Value Format
    @api.onchange('name')
    def _check_value_onchange(self):
        self.dis_name = self.name
        if self.attribute_id.is_float and self.name:
            if self.check_float_validation(value=self.name):
                self.name_float = self.name

        elif self.attribute_id.is_integer and self.name:
            if self.check_integer_validation(value=self.name):
                self.name_integer = self.name

        '''
        if self.attribute_id.is_float and self.name:
            if self.check_float_validation(value=self.name):
                if ',' in self.name:
                    self.name_float = self.name.replace(',', '')
                else:
                    self.name_float = self.name
                # tmp_fraction = str(self.name_float).split('.')

                # 1 Decimal / Fraction Point / 0.0
                # if len(tmp_fraction) == 0:
                #     upd_value = tmp_fraction[0] + '.0'
                # elif len(tmp_fraction) == 1:
                #     upd_value = str(self.name_float)
                # else:
                #     upd_value = str(tmp_fraction[0] + '.' + tmp_fraction[1][0])
                # self.name = "{:,}".format(float(upd_value))

                # 2 Decimals / Fraction Points / 0.00
                # if len(tmp_fraction[1]) == 2:
                #     self.name = "{:,}".format(self.name_float)
                # else:
                #     self.name = "{:,}".format(self.name_float) + '0'

        elif self.attribute_id.is_integer and self.name:
            if self.check_integer_validation(value=self.name):
                if ',' in self.name:
                    self.name_integer = self.name.replace(',', '')
                else:
                    self.name_integer = self.name
        '''


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    create_variant = fields.Selection(related="attribute_id.create_variant")
    is_float = fields.Boolean(related="attribute_id.is_float")
    is_integer = fields.Boolean(related="attribute_id.is_integer")
    is_related = fields.Boolean(related="attribute_id.is_related")
    is_used_desc = fields.Boolean(related="attribute_id.is_used_desc")
    is_single_value = fields.Boolean(related="attribute_id.is_single_value")
    state = fields.Selection([
        ('normal', 'Not Checked'),
        ('blocked', 'Check'),
        ('done', 'Confirmed')
    ], string='Status', copy=False, default='normal')
    note = fields.Char(related="attribute_id.note")
    sequence = fields.Integer(string="Sequence")

    # checking
    # Validate Attribute Value Name as per Float & Integer Value Format
    @api.constrains('value_ids')
    def _check_attribute_value_ids(self):
        for rec in self:
            if len(rec.value_ids) > 1 and rec.attribute_id.is_single_value:
                raise ValidationError(
                    "Could not be select more than one value for attribute {0}".format(rec.attribute_id.name))

        for attr_value in self.value_ids:
            if attr_value.attribute_id.is_float and attr_value.name:
                if self.env['product.attribute.value'].check_float_validation(value=attr_value.name):
                    attr_value.name_float = attr_value.name
                    attr_value.attribute_id.update_attr_values(
                        attr_value.attribute_id.value_ids.sorted(key=lambda r: r.name_float))
                    return True

            elif attr_value.attribute_id.is_integer and attr_value.name:
                if self.env['product.attribute.value'].check_integer_validation(value=attr_value.name):
                    attr_value.name_integer = attr_value.name
                    attr_value.attribute_id.update_attr_values(
                        attr_value.attribute_id.value_ids.sorted(key=lambda r: r.name_integer))
                    return True

    # Overwrite default function to allow adding attributes without values
    # https://github.com/odoo/odoo/blob/7d304078b4ed97d23ec84609e6aea137e8500a18/addons/product/models/product_attribute.py#L203
    @api.constrains('active', 'value_ids', 'attribute_id')
    def _check_valid_values(self):
        for ptal in self:
            for pav in ptal.value_ids:
                if pav.attribute_id != ptal.attribute_id:
                    raise ValidationError(
                        _("On the product %s you cannot associate the value %s with the attribute %s because they do not match.") %
                        (ptal.product_tmpl_id.display_name, pav.display_name, ptal.attribute_id.display_name)
                    )
        return True

    @api.onchange('value_ids')
    def _check_values_by_change_ev(self):
        if len(self.value_ids) > 1 and self.attribute_id.is_single_value:
            raise ValidationError("Could not select more than one value for attribute {0}".format(self.attribute_id.name))


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    # Replace Attribute Display Name with Custom Short Name
    def name_get(self):
        for rec in self:
            return [(value.id, "%s: %s" % (
                value.attribute_id.name_alt if value.attribute_id.name_alt else value.attribute_id.name, value.name))
                    for
                    value in self]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args and any("attribute_id.is_related" in cond for cond in args):
            filter_query = ['&', '&']
            for condition in args:
                filter_query.append(tuple(condition))
            result_ids = self._search(filter_query, limit=limit, access_rights_uid=name_get_uid)
        else:
            result_ids = self._search([], limit=limit, access_rights_uid=name_get_uid)
        ret_values = self.browse(result_ids).name_get()
        return ret_values if ret_values else []
