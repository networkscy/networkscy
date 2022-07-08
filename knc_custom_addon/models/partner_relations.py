from odoo import models, fields, api
from . import constants
import logging


class ProjectRelations(models.Model):
    _name = "project.relations"
    _description = "Project Relations"
    _order = "name"

    sequence = fields.Integer(string="Seq", related='name.sequence')
    name = fields.Many2one("project.relation.types", string="Relation Type", required=True)
    partner_id = fields.Many2one("res.partner", string="Related Partner", required=True, ondelete="cascade")
    project_id = fields.Many2one("project.project", string="Related Project")
    opportunity_id = fields.Many2one("crm.lead", string="Related Opportunity")
    note = fields.Char(string="Comments / Notes")

    # Check if Record is Company or Person & Add Domain to the Relation Types - Partner Form
    @api.onchange('name')
    def _relations_names(self):
        if self.partner_id:
            if self.partner_id.is_company:
                db_records = self.env["project.relation.types"].search([
                    ("is_company", '!=', self.name.is_company)
                ])
            else:
                db_records = self.env["project.relation.types"].search([("is_company", '=', False)])
            return {
                "domain": {
                    "name": [('id', 'in', [rec.id for rec in db_records])]
                }
            }

    # Check if Record is Company or Person & Add Domain to the Relation Types - Project Relations Form
    @api.onchange('partner_id')
    def _relations_companies(self):
        if self.partner_id:
            if self.partner_id.is_company:
                db_records = self.env["project.relation.types"].search([
                    ("is_company", '=', self.partner_id.is_company)
                ])
            else:
                db_records = self.env["project.relation.types"].search([("is_company", '=', False)])
            return {
                "domain": {
                    "name": [('id', 'in', [rec.id for rec in db_records])]
                }
            }


class ProjectRelationTypes(models.Model):
    _name = "project.relation.types"
    _description = "Project Relation Types"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Project Relation", required=True)
    is_company = fields.Boolean(string="Company Related", default=False)


class Partner(models.Model):
    _inherit = "res.partner"

    project_relations_ids = fields.One2many("project.relations", "partner_id", string="Related Projects",
                                            domain=lambda self: self._compute_domain_project_relations())
    opportunity_relations_ids = fields.One2many("project.relations", "partner_id", string="Related Opportunities",
                                                domain=lambda self: self._compute_domain_opportunities_relations())

    # Domain for Project Relations - Partner Form
    def _compute_domain_project_relations(self):
        db_records = self.env["project.relations"].search([("project_id", '!=', False)])
        return [('id', 'in', [rec.id for rec in db_records])]

    # Domain for Opportunity Relations - Partner Form
    def _compute_domain_opportunities_relations(self):
        db_records = self.env["project.relations"].search([("opportunity_id", '!=', False)])
        return [('id', 'in', [rec.id for rec in db_records])]


class Project(models.Model):
    _inherit = "project.project"

    partner_relations_ids = fields.One2many("project.relations", "project_id", string="Project Relations")


class Lead(models.Model):
    _inherit = "crm.lead"

    partner_relations_ids = fields.One2many("project.relations", "opportunity_id", string="Opportunity Relations")


# Inherit & Enhance from Module partner_multi_relation
class ResPartnerRelationType(models.Model):
    _inherit = "res.partner.relation.type"

    google_label = fields.Char(string="Google Label", required=True)
    related_google_label = fields.Char(string="Inverse Google Label", required=True)
    handle_invalid_onchange = fields.Selection(required=False)

    def write(self, values, addons=None):
        save_rec = super(ResPartnerRelationType, self).write(values)

        if addons is None and self.is_symmetric:
            update_params = {
                'name_inverse': self.name,
                'contact_type_right': self.contact_type_left,
                'related_google_label': self.google_label,
            }
            self.env[constants.RES_PARTNER_RELATION_TYPE_MODEL].search([('id', '=', self.id)])[0].write(
                update_params, addons=update_params)
        return save_rec

    @api.onchange('is_symmetric')
    def _compute_relevant_fields(self):
        if self.is_symmetric:
            self.name_inverse = self.name
            self.contact_type_right = self.contact_type_left
            self.related_google_label = self.google_label
        else:
            self.name_inverse = ""
            self.contact_type_right = ""
            self.related_google_label = ""

    @api.onchange('name')
    def _compute_relevant_name(self):
        if self.is_symmetric:
            self.name_inverse = self.name

    @api.onchange('contact_type_left')
    def _compute_relevant_type(self):
        if self.is_symmetric:
            self.contact_type_right = self.contact_type_left

    @api.onchange('google_label')
    def _compute_relevant_label_(self):
        if self.is_symmetric:
            self.related_google_label = self.google_label


class ResPartnerRelationAll(models.Model):
    _inherit = "res.partner.relation.all"

    res_model = fields.Char(required=False)
    res_id = fields.Integer(required=False)
    this_partner_id = fields.Many2one(required=False, domain=lambda self: self._compute_domain_partners())
    type_id = fields.Many2one(required=False)
    # type_selection_id = fields.Many2one(required=False)
    active = fields.Boolean(required=False)

    # create_uid = fields.Many2one('res.users', related='this_partner_id.create_uid', readonly=True, index=True)
    # write_uid = fields.Many2one('res.users', related='this_partner_id.write_uid', readonly=True, index=True)
    # create_date = fields.Datetime("Created at", related='this_partner_id.create_date', readonly=True, index=True)
    # write_date = fields.Datetime("Updated at", related='this_partner_id.write_date', readonly=True, index=True)

    @api.onchange("type_selection_id")
    def onchange_type_selection_id(self):
        pass

    def _compute_domain_partners(self):
        db_records = self.env["res.partner"].search([("id", '!=', self.id)])
        return [('id', 'in', [rec.id for rec in db_records])]

    @api.onchange('this_partner_id')
    def _relations_companies(self):
        if self.this_partner_id:
            db_records = self.env["res.partner"].search([("id", '!=', self.this_partner_id.id)])
            return {
                "domain": {
                    "name": [('id', 'in', [rec.id for rec in db_records])]
                }
            }
