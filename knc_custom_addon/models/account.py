# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

    
class account_move(models.Model):
    _inherit = 'account.move'   

    title = fields.Char()