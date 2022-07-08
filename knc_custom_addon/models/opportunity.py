# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api
from . import constants


class Lead(models.Model):
    _inherit = "crm.lead"

    # related_project_id = fields.Many2one("project.project", string="Related Project")
    # competitor_ids = fields.Many2many("crm.competitor", "opportunity_id", string="Related Competitors")
