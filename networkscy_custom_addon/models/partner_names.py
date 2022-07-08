# Code Checked & Confirmed by Panos on 23/04/2022
from odoo import models, fields, api, _


class FirstNameModel(models.Model):
    _name = "res.partner.first.name"
    _description = "First / Given Names"
    _sql_constraints = [("first_name_uniq", "unique (name)",
                         "The First Name you are trying to add already exists in the database. Please select this value from the list.")]

    name = fields.Char(string="First / Given Name", required=True)


class LastNameModel(models.Model):
    _name = "res.partner.last.name"
    _description = "Last + Maiden Names"
    _sql_constraints = [("last_name_uniq", "unique (name)",
                         "The Last / Maiden Name you are trying to add already exists in the database. Please select this value from the list.")]

    name = fields.Char(string="Last / Maiden Name", required=True)


class Partner(models.Model):
    _inherit = "res.partner"
      
    # Compute Full Name based on many2one Fields
    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        new_name = ""
        if self.first_name:
            new_name = self.first_name.name + " "
        if self.middle_name:
            new_name += self.middle_name.name + " "
        if self.last_name:
            new_name += self.last_name.name
        self.printed_name = new_name
        self.name = new_name