# Code Checked & Confirmed by Panos on ../../2022

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import *
import logging


class Partner(models.Model):
    _inherit = "res.partner"

    active = fields.Boolean(tracking=True)  # Default Field
    name = fields.Char(tracking=True)  # Default Field
    parent_id = fields.Many2one(tracking=True)  # Default Field
    company_type = fields.Selection(tracking=True)  # Default Field
    function = fields.Char(tracking=True)  # Default Field
    website = fields.Char(tracking=True)  # Default Field

    # Post Message on Chatter when Editing Contact Image on Existing Record
    def _partner_image_loggings(self, option):
        self.message_post(
            body=('● Contact <b>"Image"</b> has been ' + option), message_type='notification')

    # Post Message on Chatter when Editing Contact Image on Existing Record
    @api.model
    def write(self, values):
        if 'image_1920' in values:
            if not values["image_1920"] and self.image_1920:
                self._partner_image_loggings(option="<b>removed</b>")
            elif values["image_1920"] and self.image_1920:
                self._partner_image_loggings(option="<b>updated</b>")
            elif not self.image_1920:
                self._partner_image_loggings(option="<b>added</b>")
        upd_record = super(Partner, self).write(values)
        return upd_record


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name = fields.Char(tracking=True)  # Default Field
    barcode = fields.Char(tracking=True)  # Default Field
    hs_code = fields.Char(tracking=True)  # Default Field
    default_code = fields.Char(tracking=True)  # Default Field
    active = fields.Boolean(tracking=True)  # Default Field
    sale_ok = fields.Boolean(tracking=True)  # Default Field
    purchase_ok = fields.Boolean(tracking=True)  # Default Field
    landed_cost_ok = fields.Boolean(tracking=True)  # Default Field
    show_availability = fields.Boolean(tracking=True)  # Default Field
    website_published = fields.Boolean(tracking=True)  # Default Field
    allow_out_of_stock_order = fields.Boolean(tracking=True)  # Default Field
    has_configurable_attributes = fields.Boolean(tracking=True)  # Default Field
    description_sale = fields.Text(tracking=True)  # Default Field
    sale_line_warn_msg = fields.Text(tracking=True)  # Default Field
    description_purchase = fields.Text(tracking=True)  # Default Field
    purchase_line_warn_msg = fields.Text(tracking=True)  # Default Field
    description_picking = fields.Text(tracking=True)  # Default Field
    description_pickingin = fields.Text(tracking=True)  # Default Field
    description_pickingout = fields.Text(tracking=True)  # Default Field
    priority = fields.Selection(tracking=True)  # Default Field
    tracking = fields.Selection(tracking=True)  # Default Field
    cost_method = fields.Selection(tracking=True)  # Default Field
    service_type = fields.Selection(tracking=True)  # Default Field
    detailed_type = fields.Selection(tracking=True)  # Default Field
    expense_policy = fields.Selection(tracking=True)  # Default Field
    invoice_policy = fields.Selection(tracking=True)  # Default Field
    sale_line_warn = fields.Selection(tracking=True)  # Default Field
    purchase_method = fields.Selection(tracking=True)  # Default Field
    service_tracking = fields.Selection(tracking=True)  # Default Field
    purchase_line_warn = fields.Selection(tracking=True)  # Default Field
    purchase_requisition = fields.Selection(tracking=True)  # Default Field
    split_method_landed_cost = fields.Selection(tracking=True)  # Default Field
    uom_id = fields.Many2one(tracking=True)  # Default Field
    categ_id = fields.Many2one(tracking=True)  # Default Field
    uom_po_id = fields.Many2one(tracking=True)  # Default Field
    project_id = fields.Many2one(tracking=True)  # Default Field
    warehouse_id = fields.Many2one(tracking=True)  # Default Field
    intrastat_id = fields.Many2one(tracking=True)  # Default Field
    responsible_id = fields.Many2one(tracking=True)  # Default Field
    email_template_id = fields.Many2one(tracking=True)  # Default Field
    website_ribbon_id = fields.Many2one(tracking=True)  # Default Field
    project_template_id = fields.Many2one(tracking=True)  # Default Field
    property_stock_inventory = fields.Many2one(tracking=True)  # Default Field
    property_stock_production = fields.Many2one(tracking=True)  # Default Field
    property_account_income_id = fields.Many2one(tracking=True)  # Default Field
    intrastat_origin_country_id = fields.Many2one(tracking=True)  # Default Field
    property_account_expense_id = fields.Many2one(tracking=True)  # Default Field
    property_account_creditor_price_difference = fields.Many2one(tracking=True)  # Default Field
    price = fields.Float(tracking=True)  # Default Field
    weight = fields.Float(tracking=True)  # Default Field
    volume = fields.Float(tracking=True)  # Default Field
    sale_delay = fields.Float(tracking=True)  # Default Field
    list_price = fields.Float(tracking=True)  # Default Field
    standard_price = fields.Float(tracking=True)  # Default Field
    available_threshold = fields.Float(tracking=True)  # Default Field

    # Post Message on Chatter when Editing Product Template Attribute Lines on Existing Record

    ###############################################################################################################
    # ##############################  For Value IDs of Attribute-Line-IDs   #######################################
    ###############################################################################################################

    def print_logging_attribute_values(self, attribute_id, value_ids, option="replaced", existing_addons=None):
        previous_state = ''
        if existing_addons:
            for ex_val_id in existing_addons:
                db_value = self.env['product.attribute.value'].search([('id', '=', ex_val_id)])
                previous_state += db_value[0].name + ', '
            previous_state = previous_state[:-2]

        for db_val_id in value_ids:
            db_value = self.env['product.attribute.value'].search([('id', '=', db_val_id)])
            self.message_post(
                body=('● Attribute <b>"%s"</b> with Value(s) <b>"%s"</b> has been modified. Value <b>"%s"</b> has been ' + option)
                     % (attribute_id[0].name, previous_state, db_value[0].name if len(db_value) > 0 else ""),
                message_type='notification')

    def _check_value_ids_fr_attribute_lines(self, attribute_values, prod_tmp_line_id):
        for attr_value in attribute_values:
            list_ids = attr_value[2]
            db_prod_tmp_line_id = self.env['product.template.attribute.line'].search([('id', '=', prod_tmp_line_id)])
            exist_value_ids = [x.id for x in db_prod_tmp_line_id.value_ids]

            if len(exist_value_ids) > len(list_ids):
                diff = list(set(exist_value_ids) - set(list_ids))
                self.print_logging_attribute_values(
                    attribute_id=db_prod_tmp_line_id[0].attribute_id[0], value_ids=diff, option="<b>removed</b>",
                    existing_addons=exist_value_ids)
            elif len(exist_value_ids) < len(list_ids):
                diff = list(set(list_ids) - set(exist_value_ids))
                self.print_logging_attribute_values(
                    attribute_id=db_prod_tmp_line_id[0].attribute_id[0], value_ids=diff, option="<b>added</b>",
                    existing_addons=exist_value_ids)
            else:
                diff = list(set(list_ids) - set(exist_value_ids))
                self.print_logging_attribute_values(
                    attribute_id=db_prod_tmp_line_id[0].attribute_id[0], value_ids=diff, option="<b>replaced</b>",
                    existing_addons=exist_value_ids)

    ###############################################################################################################
    # ##############################  For Attribute of Attribute-Line-IDs   #######################################
    ###############################################################################################################

    def _check_attribute_fr_attribute_lines(self, attribute_id, value_ids):
        db_attr = self.env['product.attribute'].search([('id', '=', attribute_id)])

        values = ''
        for attr_value in value_ids:
            list_ids = attr_value[2]
            for idx in list_ids:
                db_object = self.env['product.attribute.value'].search([('id', '=', idx)])
                values += db_object[0].name + ', '

        self.message_post(
            body=('● Attribute <b>"%s"</b> has been <b>added</b> together with Value(s) <b>"%s"</b>') % (
            db_attr[0].name, values[:-2]),
            message_type='notification')

    ###############################################################################################################
    # ##############################     For State of Attribute-Line-IDs    #######################################
    ###############################################################################################################

    def _check_state_fr_attribute_lines(self, state, line_id):
        state_options = {
            'normal': 'Not Checked',
            'blocked': 'Check',
            'done': 'Confirmed'
        }
        db_prod_tmp_line_id = self.env['product.template.attribute.line'].search([('id', '=', line_id)])
        self.message_post(
            body=('● Attribute <b>"%s"</b> with Value(s) <b>"%s"</b> has been marked as <b>"%s"</b>') % (
                 db_prod_tmp_line_id[0].attribute_id.name, ", ".join([x.name for x in db_prod_tmp_line_id.value_ids]),
                 state_options[state],),
            message_type='notification')

    ###############################################################################################################
    # ##############################     For Delete of Attribute-Line-IDs    ######################################
    ###############################################################################################################

    def _check_delete_fr_attribute_lines(self, attribute_values):
        status = False
        for line in attribute_values:
            if line[0] == 2:
                rec = self.env['product.template.attribute.line'].search([('id', '=', line[1])])
                if rec and len(rec) > 0:
                    self.message_post(
                        body=('● Attribute <b>"%s"</b> has been <b>removed</b> together with Value(s) <b>"%s"</b>') % (
                            rec[0].attribute_id.name, ", ".join([val.name for val in rec[0].value_ids])),
                        message_type='notification')
                status = True

        if not status:
            self.message_post(
                body=str('● Product Attributes changed by removing line'), message_type='notification')

    ###############################################################################################################
    # #########################      Product Image Operations for Logging     #####################################
    ###############################################################################################################

    def _check_product_image_opts(self, option, value, rec_id=None):
        if option == "added":
            self.message_post(
                body=str('● Product Template <b>"Extra Product Media"</b> named <b>"%s"</b> has been <b>added</b>') %(value['name']),
                message_type='notification')
        elif option == "updated":
            chk_record = self.env['product.image'].search([('id', '=', rec_id)])
            self.message_post(
                body=str('● Product Template <b>"Extra Product Media"</b> named <b>"%s"</b> has been <b>updated</b> with value <b>"%s"</b>') % (
                    chk_record[0].name if len(chk_record) > 0 else "", ', '.join(value.keys())), message_type='notification')
        else:
            chk_record = self.env['product.image'].search([('id', '=', rec_id)])
            self.message_post(
                body=str('● Product Template <b>"Extra Product Media"</b> named <b>"%s"</b> has been <b>removed</b>') % (chk_record[0].name),
                message_type='notification')

    def _product_image_loggings(self, option):
        self.message_post(
            body=('● Product Template <b>"Image"</b> has been ' + option), message_type='notification')
        for _variant in self.product_variant_ids:
            _variant.message_post(
                body=('● Product Variant <b>"Image"</b> has been ' + option + ' from Product Template'), message_type='notification')

    def _product_custom_rel_fields_loggings(self, model, label, previous, new, option):
        output = ''
        if previous is None:
            output += ' with new values '
            for _id in new:
                output += self.env[model].search([('id', '=', _id)])[0].name + ', '
        elif new is None:
            output += ' with values '
            for obj_id in previous:
                output += obj_id.name + ', '
        else:
            if len(new) < len(previous.ids):
                output += ' with removed values '
                diff = list(set(previous.ids) - set(new))
            else:
                output += ' with new values '
                diff = list(set(new) - set(previous.ids))

            for _id in diff:
                output += self.env[model].search([('id', '=', _id)])[0].name + ', '
            output += "from previous values "
            for obj_id in previous:
                output += obj_id.name + ', '
        self.message_post(
            body=('● Product Template <b>"' + label + '"</b> has been ' + option + output[:-2]),
            message_type='notification')

    ###############################################################################################################
    # ##############################      End All Operations for Logging     ######################################
    ###############################################################################################################

    # Block user from editing Product Template when Is Lock is True
    def write(self, values):
        if any([x for x in values.keys() if x in ['description', 'website_description', 'out_of_stock_message', 'quotation_only_description']]):
            pass
        elif self.is_lock and 'is_lock' not in values:
            bypass_fields = ['priority', 'is_published']
            if not any([field for field in values.keys() if field in bypass_fields]):
                raise ValidationError('Please "Unlock" Product Template to be able to save any changes')

        ############################################################################################################
        # ################################    Logging for Attribute_Line_IDs    ####################################
        ############################################################################################################

        # Calculate Datetime difference in days
        datetime_diff = datetime.now() - self.create_date
        update_no_day = datetime_diff.days

        if update_no_day > 0 and "attribute_line_ids" in values:
            if any([x for x in values["attribute_line_ids"] if x[2] != False]):
                for line in values["attribute_line_ids"]:
                    if len(line) == 3 and type(line[2]) == dict and "attribute_id" in line[2]:
                        self._check_attribute_fr_attribute_lines(
                            attribute_id=line[2]["attribute_id"], value_ids=line[2]["value_ids"])
                        # self._check_value_ids_fr_attribute_lines(
                        #     attribute_values=line[2]["value_ids"], addon=True, attribute_id=line[2]["attribute_id"])

                    elif len(line) == 3 and type(line[2]) == dict and "value_ids" in line[2]:
                        self._check_value_ids_fr_attribute_lines(
                            attribute_values=line[2]["value_ids"], prod_tmp_line_id=line[1])
                    elif len(line) == 3 and type(line[2]) == dict and "state" in line[2]:
                        self._check_state_fr_attribute_lines(state=line[2]["state"], line_id=line[1])
                    else:
                        pass
            else:
                self._check_delete_fr_attribute_lines(attribute_values=values["attribute_line_ids"])

        ############################################################################################################
        # ################################        Logging for Image_1920        ####################################
        ############################################################################################################

        if 'image_1920' in values:
            if not values["image_1920"] and self.image_1920:
                self._product_image_loggings(option="<b>removed</b>")
            elif values["image_1920"] and self.image_1920:
                self._product_image_loggings(option="<b>updated</b>")
            elif not self.image_1920:
                self._product_image_loggings(option="<b>added</b>")

        ############################################################################################################
        # ###############################     Logging for Extra Media Image     ####################################
        ############################################################################################################

        if 'product_template_image_ids' in values and values["product_template_image_ids"]:
            for product_image_line in values["product_template_image_ids"]:
                if type(product_image_line[1]) == str and 'virtual' in product_image_line[1]:
                    self._check_product_image_opts(option="added", value=product_image_line[2])
                elif type(product_image_line[2]) == dict:
                    self._check_product_image_opts(
                        option="updated", value=product_image_line[2], rec_id=product_image_line[1])
                elif product_image_line[2] == False:
                    self._check_product_image_opts(
                        option="removed", value=product_image_line[2], rec_id=product_image_line[1])

        ############################################################################################################
        # #########################        Logging for Additional Fields        ####################################
        ############################################################################################################

        if 'accessory_product_ids' in values:
            res_model = 'product.product'
            res_label = 'Accessory Products'

            if len(self.accessory_product_ids.ids) == 0:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=None, new=values['accessory_product_ids'][0][2],
                    option="Added")
            elif len(values['accessory_product_ids'][0][2]) == 0:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=self.accessory_product_ids, new=None, option="Delete")
            else:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=self.accessory_product_ids,
                    new=values['accessory_product_ids'][0][2], option="Update")

        if 'alternative_product_ids' in values:
            res_model = 'product.template'
            res_label = 'Alternative Products'

            if len(self.alternative_product_ids.ids) == 0:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=None, new=values['alternative_product_ids'][0][2],
                    option="Added")
            elif len(values['alternative_product_ids'][0][2]) == 0:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=self.alternative_product_ids, new=None, option="Delete")
            else:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=self.alternative_product_ids,
                    new=values['alternative_product_ids'][0][2], option="Update")

        if 'public_categ_ids' in values:
            res_model = 'product.public.category'
            res_label = 'Public Categories'

            if len(self.public_categ_ids.ids) == 0:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=None, new=values['public_categ_ids'][0][2], option="Added")
            elif len(values['public_categ_ids'][0][2]) == 0:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=self.public_categ_ids, new=None, option="Delete")
            else:
                self._product_custom_rel_fields_loggings(
                    model=res_model, label=res_label, previous=self.public_categ_ids,
                    new=values['public_categ_ids'][0][2], option="Update")

        return super(ProductTemplate, self).write(values)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    barcode = fields.Char(tracking=True)  # Default Field
    default_code = fields.Char(tracking=True)  # Default Field
    active = fields.Boolean(tracking=True)  # Default Field
    volume = fields.Float(tracking=True)  # Default Field
    weight = fields.Float(tracking=True)  # Default Field
    standard_price = fields.Float(tracking=True)  # Default Field

    # Post Message on Chatter when Editing Product Image on Existing Record
    def write(self, values):
        upd_record = super(ProductProduct, self).write(values)

        if 'image_variant_1920' in values:
            if not values["image_variant_1920"] and self.image_variant_1920:
                self.message_post(
                    body=('● Product Variant <b>"Image"</b> has been <b>removed</b>'), message_type='notification')
            elif values["image_variant_1920"] and self.image_variant_1920:
                self.message_post(
                    body=('● Product Variant <b>"Image"</b> has been <b>updated</b>'), message_type='notification')
            elif not self.image_variant_1920:
                self.message_post(
                    body=('● Product Variant <b>"Image"</b> has been <b>added</b>'), message_type='notification')

        return upd_record
