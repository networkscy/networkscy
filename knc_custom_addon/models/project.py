# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api
from . import constants


class Project(models.Model):
    _inherit = "project.project"

    parent_project_id = fields.Many2one("project.project", string="Parent Project", index=True)
    related_child_projects_ids = fields.One2many("project.project", "parent_project_id", string="Related Projects")

    related_opportunities_ids = fields.Many2many("crm.lead", "opportunity_id", string="Related Opportunities")

    # related_child_projects_count = fields.Integer(string="Child Projects", default=0, compute="_related_child_projects_count")

    # def _related_child_projects_count(self):
    #     for rec in self:
    #         rec.related_child_projects_count = len(rec.related_child_projects_ids)
