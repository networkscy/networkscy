# Code Checked & Confirmed by Panos on 25/04/2022
from odoo import models, fields, api, _
from . import constants
import logging

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
# ADDRESS_FIELDS_HOME = ('street_home', 'street2_home', 'zip_home', 'city_home', 'state_id_home', 'country_id_home')


class Partner(models.Model):
    _inherit = "res.partner"

    # Work Address Fields - Default Fields
    street = fields.Char(string="Street Work", compute="_compute_street", tracking=True, store=True)
    street2 = fields.Char(string="Street 2 Work", tracking=True)  # Default Field
    zip = fields.Char(string="Post Code Work", tracking=True)  # Default Field
    city = fields.Char(string="City Work", tracking=True)  # Default Field
    state_id = fields.Many2one(string="State Work", tracking=True)  # Default Field
    country_id = fields.Many2one(string="Country Work", tracking=True)  # Default Field
    # map_work = fields.Char(string="Work Map", tracking=True)

    # Home Address Fields - Custom Fields
    # street_home = fields.Char(string="Street Home", compute="_compute_street_home", tracking=True, store=True)
    # street2_home = fields.Char(string="Street 2 Home", tracking=True)
    # zip_home = fields.Char(string="Post Code Home", tracking=True)
    # city_home = fields.Char(string="City Home", tracking=True)
    # state_id_home = fields.Many2one("res.country.state", string="State Home", tracking=True)
    # country_id_home = fields.Many2one("res.country", string="Country Home", tracking=True)
    # map_home = fields.Char(string="Home Map", tracking=True)

    # Auto Sync Fields for Work & Home Addresses
    # sync_work_add = fields.Boolean(string='Sync Work Address', default=False, help='Sync Work Address from Related Company')
    # sync_home_add = fields.Boolean(string='Sync Home Address', default=False, help='Sync Home Address from Related Company')

    # Auto Complete Address Fields for Work & Home Addresses
    zip_id = fields.Many2one(comodel_name="res.city.zip", string="Post Code Work Lookup", index=True,
                             compute="_compute_zip_id", readonly=False, store=True) # Existing Field from base_location
    # zip_id_home = fields.Many2one(comodel_name="res.city.zip", string="Post Code Home Lookup",
                                  # index=True, readonly=False, store=True) # Custom Field from knc_custom_addon

    # Auto Complete Address Fields for Work & Home Addresses with Street Names
    street_zip_id = fields.Many2one(comodel_name="res.partner.street", string="Post Code Work Lookup with Street",
                                    index=True, readonly=False, store=True) # Custom Field from knc_custom_addon
    # street_zip_id_home = fields.Many2one(comodel_name="res.partner.street", string="Post Code Home Lookup with Street",
                                         # index=True, readonly=False, store=True) # Custom Field from knc_custom_addon

    # Inverse Relation Field
   # inverse_relation_ids = fields.One2many(constants.RES_PARTNER_RELATION_ALL_MODEL, 'other_partner_id', string='Inverse Relation')


    # Auto Complete Custom Home Address Fields based on the Custom Field zip_id_home
    # This is a similar action of the field zip_id from module base_location but for Home Fields
    # @api.onchange("zip_id_home") # Checked 25/04/2022
    # def _compute_zip_id_home(self):
        # for record in self:
            # if record.zip_id_home:
                # record.city_home = record.zip_id_home.city_id.name
                # record.state_id_home = record.zip_id_home.state_id
                # record.zip_home = record.zip_id_home.name
                # record.country_id_home = record.zip_id_home.country_id


    # Auto Complete Work Address Fields based on the Custom Street Field street_zip_id
    # This is a similar action of the field zip_id from module base_location but includes the Street Names
    @api.onchange("street_zip_id") # Checked 25/04/2022
    def _compute_street(self):
        for record in self:
            if record.street_zip_id:
                record.street = record.street_zip_id.street
                record.city = record.street_zip_id.zip_id.city_id.name
                record.state_id = record.street_zip_id.zip_id.state_id
                record.zip = record.street_zip_id.zip_id.name
                record.country_id = record.street_zip_id.zip_id.country_id


    # Auto Complete Home Address Fields based on the Custom Street Field street_zip_id
    # This is a similar action of the field zip_id from module base_location but includes the Street Names
    # @api.onchange("street_zip_id_home") # Checked 25/04/2022
    # def _compute_street_home(self):
        # for record in self:
            # if record.street_zip_id_home:
                # record.street_home = record.street_zip_id_home.street
                # record.city_home = record.street_zip_id_home.zip_id.city_id.name
                # record.state_id_home = record.street_zip_id_home.zip_id.state_id
                # record.zip_home = record.street_zip_id_home.zip_id.name
                # record.country_id_home = record.street_zip_id_home.zip_id.country_id


    # Sync Work Address Fields from Parent Contact
    # @api.onchange('sync_work_add') # Checked 25/04/2022
    # def sync_work_address(self):
        # if self.sync_work_add and self.parent_id:
            # self.street = self.parent_id.street
            # self.street2 = self.parent_id.street2
            # self.city = self.parent_id.city
            # self.state_id = self.parent_id.state_id
            # self.zip = self.parent_id.zip
            # self.country_id = self.parent_id.country_id
            # self.map_work = self.parent_id.map_work


    # Sync Home Address Fields from Parent Contact
    # @api.onchange('sync_home_add') # Checked 25/04/2022
    # def sync_home_address(self):
        # if self.sync_home_add and self.parent_id:
            # self.street_home = self.parent_id.street_home
            # self.street2_home = self.parent_id.street2_home
            # self.city_home = self.parent_id.city_home
            # self.state_id_home = self.parent_id.state_id_home
            # self.zip_home = self.parent_id.zip_home
            # self.country_id_home = self.parent_id.country_id_home
            # self.map_home = self.parent_id.map_home


    # Clean Values of the Lookup Fields used for Auto Completion of the Work & Home Address Fields
    def remove_auto_address_field(self, values): # Checked 25/04/2022
        if 'zip_id' in values:
            del values['zip_id']
        if 'street_zip_id' in values:
            del values['street_zip_id']
        if 'zip_id_home' in values:
            del values['zip_id_home']
        if 'street_zip_id_home' in values:
            del values['street_zip_id_home']
        return values

    # Clean Values of the Lookup Fields & Sync Addresses of the Child Contacts
    def write(self, values): # Checked 25/04/2022
        values = self.remove_auto_address_field(values)
        save_record = super(Partner, self).write(values)

        _logging = logging.getLogger(__name__)
        try:
            company_contact = self.env[constants.RES_PARTNER_MODEL].search([('id', '=', self.id)])
            if company_contact and len(company_contact) > 0 and company_contact[0].is_company:
                co_related_contacts = self.env[constants.RES_PARTNER_MODEL].search([
                    ('parent_id', '=', company_contact[0].id)
                ])
                for _contact in co_related_contacts:
                    if _contact.sync_work_add:
                        self.update_address_params(sel_contact=_contact, parent_contact=company_contact[0])
                    if _contact.sync_home_add:
                        self.update_address_params(sel_contact=_contact, parent_contact=company_contact[0], child_address=True)
        except:
            pass

        return save_record


    # Sync Work & Home Address Fields from Parent Contact when Saving Parent Contact
    # @api.model # Checked 25/04/2022
    # def update_address_params(self, sel_contact, parent_contact, child_address=False):
        # if not child_address:
            # update_query = "update " + constants.RES_PARTNER_STASH_MODEL + " set " + \
                           # "street='" + str(parent_contact.street if parent_contact.street else '') + \
                            # "',street2='" + str(parent_contact.street2 if parent_contact.street2 else '') + \
                            # "',city='" + str(parent_contact.city if parent_contact.city else '') + \
                            # "',state_id=" + str(parent_contact.state_id.id if parent_contact.state_id else 0) + \
                            # ",zip='" + str(parent_contact.zip if parent_contact.zip else '') + \
                            # "',country_id=" + str(parent_contact.country_id.id if parent_contact.country_id else 0) + \
                            # ",map_work='" + str(parent_contact.map_work if parent_contact.map_work else '') + \
                            # "' where id=" + str(sel_contact.id)
        # else:
            # update_query = "update " + constants.RES_PARTNER_STASH_MODEL + " set " + \
                            # "street_home='" + str(parent_contact.street_home if parent_contact.street_home else '') + \
                            # "',street2_home='" + str(parent_contact.street2_home if parent_contact.street2_home else '') + \
                            # "',city_home='" + str(parent_contact.city_home if parent_contact.city_home else '') + \
                            # "',state_id_home=" + str(parent_contact.state_id_home.id if parent_contact.state_id_home else 0) + \
                            # ",zip_home='" + str(parent_contact.zip_home if parent_contact.zip_home else '') + \
                            # "',country_id_home=" + str(parent_contact.country_id_home.id if parent_contact.country_id_home else 0) + \
                            # ",map_home='" + str(parent_contact.map_home if parent_contact.map_home else '') + \
                            # "' where id=" + str(sel_contact.id)
        # self.env.cr.execute(update_query)