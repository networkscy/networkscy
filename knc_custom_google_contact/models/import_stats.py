from odoo import models, fields
from . import constants


class ImportDataStats(models.Model):
    _name = constants.GOOGLE_MOD_IMPORT_STATS_MODEL
    _description = "Google Connector Import History"

    connector = fields.Many2one(constants.GOOGLE_MOD_CONNECTOR_MODEL)
    new_contact = fields.Integer(string="Created")
    update_contact = fields.Integer(string="Updated")
    contact_ids = fields.Many2many(constants.RES_PARTNER_MODEL, 'imp_res_id', 'imp_con_id', string="Related Contacts")
