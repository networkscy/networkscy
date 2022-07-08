from odoo import models, fields

# ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
# ADDRESS_FIELDS_HOME = ('street_home', 'street2_home', 'zip_home', 'city_home', 'state_id_home', 'country_id_home')


class Partner(models.Model):
    _inherit = "res.partner"

    active_sync = fields.Boolean(string="Sync to Google", default=False, tracking=True)

    first_name = fields.Many2one("res.partner.first.name", string="First / Given Name")
    middle_name = fields.Many2one("res.partner.last.name", string="Maiden Name")
    last_name = fields.Many2one("res.partner.last.name", string="Last Name")
    is_family = fields.Boolean(string="Is a Family", default=False)

    mobile = fields.Char(string="Mobile Phone", tracking=True)  # Default Field
    phone = fields.Char(string="Work Phone", tracking=True)  # Default Field
    phone_business = fields.Char(string="Business Phone", tracking=True)
    phone_other = fields.Char(string="Other Phone", tracking=True)
    phone_company = fields.Char(string="Company Phone", tracking=True)

    email = fields.Char(string="Work Email", tracking=True)  # Default Field
    email_personal = fields.Char(string="Personal Email", tracking=True)
    email_other = fields.Char(string="Other Email", tracking=True)
    email_alternate = fields.Char(string="Alternate Email", tracking=True)

    printed_name = fields.Char(string="Printed Name", tracking=True)
    birthday = fields.Date(string="Birthday", tracking=True)
    id_no = fields.Char(string="ID #", tracking=True)
    vat = fields.Char(string="VAT / Reg. #", tracking=True)  # Default Field
    reg_date = fields.Date(string="Reg. Date", tracking=True)

    id_x = fields.Integer(string='IDx')  # Temporary Previous ID

    status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked', 'Checked')],
        string='Status', default='draft', copy=False, tracking=True)
