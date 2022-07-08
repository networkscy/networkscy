from odoo import models, fields
from . import constants


class ResPartnerCategoryModel(models.Model):
    _inherit = constants.RES_PARTNER_CATEGORY_MODEL

    gc_name = fields.Char('CMG Name')
    gc_res_id = fields.Char("Membership Group")
