# Code Checked & Confirmed by Panos on ../../2022
from odoo import models, fields, api
from . import constants
import logging


class Competitor(models.Model):
    _name = "crm.competitor"
    _description = "Competitors"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Competitor Name", compute="_compute_name_field")
    partner_id = fields.Many2one("res.partner", string="Related Partner", required=True, ondelete="cascade")
    logo = fields.Binary(string="Competitor Logo", related="partner_id.image_1920")
    child_contact_ids = fields.Many2many(
        "res.partner", "res_partner_competitor_rel", "res_id", "cmp_id", string="Related Contacts",
        compute="_compute_child_contacts")
    competitor_project_ids = fields.One2many("crm.competitor.projects", "competitor_id", string="Related Projects")
    competitor_opportunity_ids = fields.One2many(
        "crm.competitor.opportunities", "competitor_id", string="Related Opportunities")
    type = fields.Selection(selection=[
        ('direct', 'Primary / Direct'),
        ('indirect', 'Secondary / Indirect'),
        ('replacement', 'Replacement / Phantom')],
        string="Type", tracking=True)
    threat = fields.Selection(selection=[
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')],
        string="Threat Level", tracking=True)
    competitor_ids = fields.Many2one("crm.competitor", string="Related Competitors")
    brands_ids = fields.Many2many("crm.competitor.brands", "competitor_ids", string="Brands")
    sectors_ids = fields.Many2many("crm.competitor.sectors", string="Sectors")
    industries_ids = fields.Many2many("crm.competitor.industries", string="Industries")
    notes = fields.Char(string="Comments / Notes")

    @api.onchange('partner_id')
    def _compute_filter_partner(self):
        ex_res_partner_ids= []
        crm_cmp_records = self.env[self._name].search([])
        for record in crm_cmp_records:
            ex_res_partner_ids.append(record.partner_id.id)

        return {
            "domain": {
                "partner_id": ['&', ('is_company', '=', True), ('id', 'not in', ex_res_partner_ids)]
            }
        }

    @api.depends('partner_id.name')
    def _compute_name_field(self):
        for rec in self:
            if not rec.name:
                rec.partner_id.write({'is_competitor': True})
                rec.name = rec.partner_id.name

    def _compute_child_contacts(self):
        if self.partner_id:
            child_partners = self.env["res.partner"].search([("parent_id", '=', self.partner_id.id)])
            self.child_contact_ids = [(6, 0, [rec.id for rec in child_partners])]

    @api.model
    def unlink(self, values):
        for cid in values:
            rec = self.env['crm.competitor'].search([('id', '=', cid)])
            if rec and len(rec) > 0:
                rec[0].partner_id.write({'is_competitor': False})
            self.env.cr.execute('delete from crm_competitor where id={0}'.format(cid))
        return super(Competitor, self).unlink()


class CompetitorBrands(models.Model):
    _name = "crm.competitor.brands"
    _description = "Competitor Brands"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Brand Name", required=True)
    logo = fields.Binary(string="Brand Logo")
    origin = fields.Many2one("res.country", string="Brand Origin")
    website = fields.Char(string="Brand Website")
    partner_id = fields.Many2one("res.partner", string="Related Partner", domain="[('is_company', '=', True)]", ondelete="restrict")
    notes = fields.Char(string="Comments / Notes")
    common_brand = fields.Boolean(string="Common Brand", default=False, tracking=True)
    related_competitors_ids = fields.Many2many("crm.competitor", "competitor_ids", string="Related Competitors")


class CompetitorSectors(models.Model):
    _name = "crm.competitor.sectors"
    _description = "Competitor Sectors"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Sector Name", required=True)


class CompetitorIndustries(models.Model):
    _name = "crm.competitor.industries"
    _description = "Competitor Industries"
    _order = "sequence"

    sequence = fields.Integer(string="Seq", default=1, required=True)
    name = fields.Char(string="Industry Name", required=True)


class CompetitorProjects(models.Model):
    _name = "crm.competitor.projects"
    _description = "Competitor Projects"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "competitor_id"

    competitor_id = fields.Many2one("crm.competitor", string="Related Competitor", required=True, ondelete="cascade")
    competitor_contacts_ids = fields.Many2many(
        "res.partner", "res_competitor_project_rel", "res_id", "project_id",
        compute="_compute_competitor_contacts_ids", inverse='_set_competitor_wrt_contact_ids',
        string="Competitor Contacts", store=True)
    competitor_brands_ids = fields.Many2many(
        "crm.competitor.brands", "brand_competitor_project_rel", "brand_id", "project_id",
        compute="_compute_competitor_brands_ids", inverse='_set_competitor_wrt_brand_ids', string="Competitor Brands",
        store=True)
    project_id = fields.Many2one("project.project", string="Related Project", required=True)
    project_stage_id = fields.Many2one(
        "project.project.stage", string="Project Stage", compute="_compute_project_stage")
    notes = fields.Char(string="Comments / Notes", tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", related="project_id.company_id.currency_id")
    price_value = fields.Float(string="Price Value", tracking=True)
    price_date = fields.Date(string="Price Date", tracking=True)
    source_id = fields.Many2one("res.partner", string="Source Contact", tracking=True)
    quality = fields.Selection(selection=[
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')],
        string="Quality Level", tracking=True)

    ##############################################################################################################
    # ###########################    Compute for Contact IDs wrt Competitor ID   #################################
    ##############################################################################################################

    def _set_competitor_wrt_contact_ids(self):
        pass

    @api.depends('competitor_id')
    def _compute_competitor_contacts_ids(self):
        for rec in self:
            if rec.competitor_id:
                child_partners = self.env["res.partner"].search([("parent_id", '=', rec.competitor_id.partner_id.id)])
                rec.competitor_contacts_ids = [(6, 0, [rec.id for rec in child_partners])]
            else:
                rec.competitor_contacts_ids = [(6, 0, [])]

    ##############################################################################################################
    # ###########################     Compute for Brand IDs wrt Competitor ID      ###############################
    ##############################################################################################################

    def _set_competitor_wrt_brand_ids(self):
        pass

    @api.depends('competitor_id')
    def _compute_competitor_brands_ids(self):
        for rec in self:
            if rec.competitor_id:
                rec.competitor_brands_ids = [(6, 0, [rec.id for rec in self.competitor_id.brands_ids])]
            else:
                rec.competitor_brands_ids = [(6, 0, [])]

    ##############################################################################################################
    # ###########################      Runtime domain calculation with fields      ###############################
    ##############################################################################################################

    @api.onchange('competitor_id', 'competitor_contacts_ids', 'competitor_brands_ids')
    def _compute_domain_addon(self):
        if self.competitor_id:
            child_partners = self.env["res.partner"].search([("parent_id", '=', self.competitor_id.partner_id.id)])
            return {
                "domain": {
                    "competitor_contacts_ids": [("id", "in", [rec.id for rec in child_partners])],
                    "competitor_brands_ids": [("id", "in", [rec.id for rec in self.competitor_id.brands_ids])]
                }
            }

    def _compute_project_stage(self):
        try:
            if self.project_id:
                self.project_stage_id = self.project_id.stage_id
            else:
                self.project_stage_id = None
        except:
            self.project_stage_id = None


class CompetitorOpportunities(models.Model):
    _name = "crm.competitor.opportunities"
    _description = "Competitor Opportunities"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "competitor_id"

    competitor_id = fields.Many2one("crm.competitor", string="Related Competitor", required=True, ondelete="cascade")
    competitor_contacts_ids = fields.Many2many(
        "res.partner", "res_competitor_opportunity_rel", "res_id", "opportunity_id",
        compute="_compute_competitor_contacts_ids", inverse='_set_competitor_wrt_contact_ids',
        string="Competitor Contacts", store=True)
    competitor_brands_ids = fields.Many2many(
        "crm.competitor.brands", "brand_competitor_opportunity_rel", "brand_id", "opportunity_id",
        compute="_compute_competitor_brands_ids", inverse='_set_competitor_wrt_brand_ids', string="Competitor Brands",
        store=True)
    opportunity_id = fields.Many2one("crm.lead", string="Related Opportunity", required=True)
    opportunity_stage_id = fields.Many2one(
        "crm.stage", string="Opportunity Stage", compute="_compute_opportunity_stage")
    notes = fields.Char(string="Comments / Notes", tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", related="opportunity_id.company_id.currency_id")
    price_provided = fields.Float(string="Provided Price", tracking=True)
    price_date = fields.Date(string="Price Date", tracking=True)
    source_id = fields.Many2one("res.partner", string="Source Contact", tracking=True)
    threat = fields.Selection(selection=[
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')],
        string="Threat Level", tracking=True)

    ##############################################################################################################
    # ###########################    Compute for Contact IDs wrt Competitor ID   #################################
    ##############################################################################################################

    def _set_competitor_wrt_contact_ids(self):
        pass

    @api.depends('competitor_id')
    def _compute_competitor_contacts_ids(self):
        for rec in self:
            if rec.competitor_id:
                child_partners = self.env["res.partner"].search([("parent_id", '=', rec.competitor_id.partner_id.id)])
                rec.competitor_contacts_ids = [(6, 0, [rec.id for rec in child_partners])]
            else:
                rec.competitor_contacts_ids = [(6, 0, [])]

    ##############################################################################################################
    # ###########################     Compute for Brand IDs wrt Competitor ID      ###############################
    ##############################################################################################################

    def _set_competitor_wrt_brand_ids(self):
        pass

    @api.depends('competitor_id')
    def _compute_competitor_brands_ids(self):
        for rec in self:
            if rec.competitor_id:
                rec.competitor_brands_ids = [(6, 0, [rec.id for rec in self.competitor_id.brands_ids])]
            else:
                rec.competitor_brands_ids = [(6, 0, [])]

    ##############################################################################################################
    # ###########################      Runtime domain calculation with fields      ###############################
    ##############################################################################################################

    @api.onchange('competitor_id', 'competitor_contacts_ids', 'competitor_brands_ids')
    def _compute_domain_addon(self):
        if self.competitor_id:
            child_partners = self.env["res.partner"].search([("parent_id", '=', self.competitor_id.partner_id.id)])
            return {
                "domain": {
                    "competitor_contacts_ids": [("id", "in", [rec.id for rec in child_partners])],
                    "competitor_brands_ids": [("id", "in", [rec.id for rec in self.competitor_id.brands_ids])]
                }
            }

    def _compute_opportunity_stage(self):
        try:
            if self.opportunity_id:
                self.opportunity_stage_id = self.opportunity_id.stage_id
            else:
                self.opportunity_stage_id = None
        except:
            self.opportunity_stage_id = None


class Project(models.Model):
    _inherit = "project.project"

    competitor_ids = fields.One2many("crm.competitor.projects", "project_id", string="Related Competitors")


class Lead(models.Model):
    _inherit = "crm.lead"

    competitor_ids = fields.One2many("crm.competitor.opportunities", "opportunity_id", string="Related Competitors")


class Partner(models.Model):
    _inherit = "res.partner"

    is_competitor = fields.Boolean(
        string="Is a Competitor", default=False, compute="_compute_competitor_val", store=True)

    def _compute_competitor_val(self):
        try:
            records = self.env["crm.competitor"].search([('partner_id', '=', self.id)])
            if records and len(records) > 0:
                self.is_competitor = True
            else:
                self.is_competitor = False
        except:
            self.is_competitor = False

    def read(self, fields=None, load='_classic_read'):
        ret_records = super(Partner, self).read(fields=fields, load=load)
        if fields and 'display_name' in fields:
            for rec in ret_records:
                rec["display_name"] = rec["display_name"].split(',')[1] \
                    if ',' in rec["display_name"] else rec["display_name"]
        return ret_records
