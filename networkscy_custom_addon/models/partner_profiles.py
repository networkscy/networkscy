# Code Checked & Confirmed by Panos on 23/04/2022
from odoo import models, fields, api
from . import constants


class SocialProfiles(models.Model):
    _name = "social.profiles"
    _description = "Social Profiles"
    _order = "name"

    sequence = fields.Integer(string="Seq", related="sp_type.sequence")
    name = fields.Char(string="Profile Link", required=True)
    sp_type = fields.Many2one("social.profile.types", string="Profile Type", required=True)
    sp_partner_id = fields.Many2one("res.partner", string="Related Partner")


class SocialProfileTypes(models.Model):
    _name = "social.profile.types"
    _description = "Social Profile Types"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Profile Name", required=True)
    label = fields.Char(string="Profile Label", required=True)

    @api.model
    def create(self, values):
        save_rec = super(SocialProfileTypes, self).create(values)
        for each in save_rec:
            if not each.label:
                each.write({'label': each.name})
        return save_rec


class Partner(models.Model):
    _inherit = "res.partner"

    social_profiles_ids = fields.One2many("social.profiles", 'sp_partner_id', string="Social Profiles")