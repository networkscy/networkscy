# Code Checked & Confirmed by Panos on 24/04/2022
from odoo import models, fields, api, _
from . import constants
import logging


class ContactStreetModel(models.Model):
    _name = "res.partner.streets"
    _description = "Street Names"

    name = fields.Char(compute="_compute_new_display_name", store=True, index=True)
    street = fields.Char(string="Street Name")
    limits = fields.Char(string="Street Limits")
    country_id = fields.Many2one(constants.RES_COUNTRY_MODEL, string="Country")
    zip = fields.Char(string="Post Code")
    zip_id = fields.Many2one("res.city.zip", string="Post Code Info")
    identity = fields.Integer(string="#")


    # Change Display Name to be used by the 'street_zip_id' & 'street_zip_id_home' autocomplete fields
    @api.depends("street", "zip_id", "zip_id.name", "zip_id.city_id", "zip_id.state_id", "zip_id.country_id", "limits")
    def _compute_new_display_name(self):
        for rec in self:
            name = [rec.street, rec.zip_id.name]
            if rec.zip_id.city_id:
                name.append(rec.zip_id.city_id.name)
            if rec.zip_id.state_id:
                name.append(rec.zip_id.state_id.name)
            if rec.zip_id.country_id:
                name.append(rec.zip_id.country_id.name)
            if rec.limits:
                name.append(rec.limits)
            try:
                rec.name = ", ".join(name)
            except:
                pass


    # Search Post Code & Autofill Country
    @api.onchange('zip')
    def _map_zip_id(self):
        country_ids = []
        if self.zip:
            zip_ids = self.get_filter_zip_id(zip_code=self.zip)
            if zip_ids and len(zip_ids) > 0:
                self.zip_id = zip_ids[0]
                self.country_id = zip_ids[0].country_id
                country_ids = [zip_id.country_id.id for zip_id in zip_ids]
            else:
                self.zip_id = None
                self.country_id = None

        filter_domain = [('id', 'in', country_ids)]
        result = {
            'domain': {
                'country_id': filter_domain,
            },
        }
        return result


    # Update Display Name on Country Selection
    @api.onchange('country_id')
    def _map_zip_country_id(self):
        if self.zip:
            zip_ids = self.get_filter_zip_id(zip_code=self.zip, country_id=self.country_id)
            if zip_ids and len(zip_ids) > 0:
                self.zip_id = zip_ids[0]


    @api.model
    def create(self, values):
        save_recs = super(ContactStreetModel, self).create(values)
        for each in save_recs:
            chk_exist = self.env[constants.RES_CITY_ZIP_MODEL].search([('name', '=', each.zip)])
            if chk_exist and len(chk_exist) > 0:
                self._update_zip_id(obj=each, rec=chk_exist[0])
        return save_recs


    def write(self, values):
        if 'zip' in values or 'country_id' in values:
            country_id = self.country_id
            zip_val = self.zip

            if 'zip' in values:
                zip_val = self.zip
            if 'country_id' in values:
                country_id = values["country_id"]

            resp = self.get_filter_zip_id(zip_code=zip_val, country_id=country_id)
            if resp is None:
                values["zip_id"] = None
                values["name"] = ""
            else:
                values["zip_id"] = resp[0]
        return super(ContactStreetModel, self).write(values)


    def get_filter_zip_id(self, zip_code, country_id=None):
        response, filter_query = None, []
        if country_id:
            filter_query.append('&')
            try:
                filter_query.append(('country_id', '=', country_id.id))
            except:
                filter_query.append(('country_id', '=', country_id))
        filter_query.append(('name', '=', zip_code))
        chk_exist = self.env[constants.RES_CITY_ZIP_MODEL].search(filter_query)
        if chk_exist and len(chk_exist) > 0:
            response = chk_exist
        return response


    # Update Display Name with Street Details
    def _update_zip_id(self, obj, rec):
        display_name = [rec.name]
        if obj.street:
            display_name.append(obj.street)
        if rec.city_id:
            display_name.append(rec.city_id.name)
        if rec.state_id:
            display_name.append(rec.state_id.name)
        if rec.country_id:
            display_name.append(rec.country_id.name)
        if obj.limits:
            display_name.append(obj.limits)

        upd_query = "update " + res.partner.streets + " set zip_id=" + str(rec.id) + \
                    ", name='" + ', '.join(display_name) + "' where id=" + str(obj.id)
        self.env.cr.execute(upd_query)