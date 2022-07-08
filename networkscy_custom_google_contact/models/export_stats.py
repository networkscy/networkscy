from odoo import models, fields
from . import constants


class ExportDataStats(models.Model):
    _name = constants.GOOGLE_MOD_EXPORT_STATS_MODEL
    _description = "Google Connector Export History"

    connector = fields.Many2one(constants.GOOGLE_MOD_CONNECTOR_MODEL)
    new_contact = fields.Integer(string="Created")
    update_contact = fields.Integer(string="Updated")
    contact_ids = fields.Many2many(constants.RES_PARTNER_MODEL, 'exp_res_id', 'exp_con_id', string="Related Contacts")
