# Code Checked & Confirmed by Panos on ../../2022
# https://bitbucket.org/kncltd/addons_custom_10/src/master/knc_extension/models/waybill.py

from odoo import fields, models, api, _


class WayBillsModel(models.Model):
    _name = 'way.bill'
    _description = 'KNC Waybills'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "waybill_date asc"

    waybill_date = fields.Datetime(
        string='Transfer Date', copy=False, tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    issued_by_id = fields.Many2one(
        'res.users', string='Issued by', required=True, default=lambda self: self.env.user.id, copy=False,
        tracking=True, states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    issued_date = fields.Datetime(
        string='Issued Date', required=True, default=fields.Datetime.now, copy=False, tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})

    delivered_by_id = fields.Many2one(
        'res.partner', string='Processed by', copy=False, tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    received_by = fields.Char(
        string='Received by', tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})

    received_by_company = fields.Char(
        string='On Behalf of', tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    received_by_phone = fields.Char(
        string='Contact Phone', tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})

    contact_id_find = fields.Many2one(
        'res.partner', string='Contact Lookup',
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    waybill_type = fields.Selection([
        ('delivery', 'Delivery to Project'), ('pickup', 'Pickup from KNC'), ('courier', 'Delivery to Courier'),
        ('dropship', 'Drop Shipment to Project'), ('return_w', 'Return'),
    ], string='Waybill Type', default='delivery', copy=False, tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})

    note_ref = fields.Char(
        string='Waybill Reference', tracking=True, copy=False,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    partner_id = fields.Many2one(
        'res.partner', string='Related Partner', index=True, tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    contact_id = fields.Many2one(
        'res.partner', string='Contact Person', tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})

    project_id = fields.Many2one(
        'project.project', string='Related Project', required=False,
        tracking=True, states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    order_id = fields.Many2one(
        'sale.order', string='Related Sales Order', required=False, tracking=True,
        states={'archived': [('readonly', False)], 'converted': [('readonly', True)]})
    bill_lines = fields.One2many('way.bill.lines', 'bill_id', string="Waybill Lines", tracking=True)
    company_id = fields.Many2one('res.company', string='Company', tracking=True)

    invoice_status = fields.Selection(string='Invoice Status', related='order_id.invoice_status', readonly=True)

    # Not found in V15 about delivery_status
    delivery_status = fields.Selection(string='Delivery Status', related='order_id.state', readonly=True)

    name = fields.Char(string='Waybill #', required=True, default="New", copy=False)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('prepared', 'Picking & Packing'),
        ('progress', 'Ready for Pickup'),
        ('delivering', 'Delivering to Site'),
        ('proof', 'Waiting for Proof'),
        ('archived', 'Scanned & Archived'),
        ('converted', 'Converted to Transfer')],
        string='Waybill State', default='draft', copy=False, tracking=True, readonly=False)
    checked_state = fields.Selection(selection=[
        ('not_started', 'Not Checked'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Waiting / Blocked'),
        ('assistance', 'Needs Assistance'),
        ('approval', 'Needs Approval'),
        ('checked', 'Waybill Checked')],
        string='Check Status', copy=False, tracking=True, readonly=False)
    tracking = fields.Char(
        string='Courier Tracking #', copy=False, tracking=True,
        states={'archived': [('readonly', True)], 'converted': [('readonly', True)]})
    picking_ids = fields.Many2many(
        'stock.picking', 'picking_waybill_rel', 'picking_id', 'bill_id',
        string='Rltd Transfers', copy=False, tracking=True)

    class_ref = fields.Char(string='SO Class / Reference', compute='_get_order_ref', copy=False)
    note = fields.Text(string='Internal Notes', copy=False, tracking=True)
    proof = fields.Binary(string='Scanned Proof', copy=False, tracking=True)
    proof_name = fields.Char(string='Proof Name', copy=False, tracking=True)
    file_name = fields.Char(string='File Name', compute='_get_file_name', copy=False)
    product_id = fields.Many2one('product.product', related='bill_lines.product_id', string="Product")
    active = fields.Boolean(default=True, tracking=True)
    lock_transfer = fields.Boolean(string='Lock', copy=False, default=False, tracking=True)
    hide_action_buttons = fields.Boolean(string='Hide Action Buttons', compute='_compute_hide_action_buttons')
    lot_ids = fields.Many2many('stock.production.lot', string='LOT / Serial Number', related='bill_lines.lot_id')

    # Lock Stock Transfers / Operation
    @api.model
    def button_lock(self):
        for rec in self:
            rec.lock_transfer = True

    # Unlock Stock Transfers / Operation
    @api.model
    def button_unlock(self):
        for rec in self:
            rec.lock_transfer = False

    # Hide Action Buttons - Edit / Create - when Locked
    @api.depends('lock_transfer')
    def _compute_hide_action_buttons(self):
        for rec in self:
            if rec.lock_transfer == False:
                # Show Create/Edit buttons on draft
                rec.hide_action_buttons = False
            elif rec.lock_transfer == True:
                # Hide Create/Edit buttons if order is done
                rec.hide_action_buttons = True

    # Retrieve Waybill Create By & Date
    @api.model
    def update_dates(self):
        for rec in self:
            rec.issued_by_id = rec.create_uid
            rec.issued_date = rec.create_date
            self.message_post(body=" > > > `Update Issued By & Date` is clicked - Issued By & Date = Created By & Date",
                              message_type='comment', author_id=self.env.user.partner_id.id)

    @api.depends('order_id')
    def _get_order_ref(self):
        for rec in self:
            ref = 'Class / Reference / Date Modified'
            if rec.order_id:
                if rec.order_id.class_id:
                    ref = rec.order_id.class_id.name
                if rec.order_id.client_order_ref:
                    ref += ' / ' + rec.order_id.client_order_ref
                if rec.order_id.write_date:
                    ref += ' / ' + rec.order_id.write_date
            rec.class_ref = ref

    # Waybill Proof File Name
    @api.depends('waybill_date', 'name', 'note_ref', 'company_id')
    def _get_file_name(self):
        for rec in self:
            if rec.waybill_date:
                filen = 'KNC Waybill '
                filen += rec.waybill_date[:10].replace('-', '.') + ' - '
                filen += rec.name.replace('/', '.')
                if rec.note_ref:
                    filen += ' - ' + rec.note_ref or ''
                if rec.company_id and rec.company_id.code_name:
                    filen += ' [' + rec.company_id.code_name + ']'
                rec.file_name = filen
            else:
                rec.file_name = ""

    @api.onchange('contact_id_find')
    def onchange_contact_id(self):
        if self.contact_id_find:
            self.received_by = self.contact_id_find.dis_name
            self.received_by_company = self.contact_id_find.parent_id and self.contact_id_find.parent_id.dis_name or False
            self.received_by_phone = self.contact_id_find.mobile or self.contact_id_find.mobile_per or False

    @api.onchange('order_id')
    def onchange_order_id(self):
        if self.order_id:
            self.partner_id = self.order_id.partner_id
            self.contact_id = self.order_id.contact_id or False
            self.project_id = self.order_id.new_project_id or False
            # self.partner_shipping_id = self.order_id.partner_shipping_id or False
            # self.note_ref = self.order_id.client_order_ref or False

    @api.onchange('waybill_type')
    def onchange_waybill_type(self):
        if self.waybill_type:
            # Delivery to Project
            if self.waybill_type == 'delivery':
                return {'domain': {'partner_shipping_id': [('is_courier', '!=', True)],
                                   'delivered_by_id': [('supplier', '!=', True), ('is_courier', '!=', True),
                                                       ('is_company', '!=', True)]},
                        'value': {'partner_shipping_id': False, 'delivered_by_id': False}}
            # Pickup from KNC - ok
            own_company_add = self.env['res.partner'].search([('name', '=', 'KNC')])
            if self.waybill_type == 'pickup':
                return {'domain': {'partner_shipping_id': [('id', '=', own_company_add.id)],
                                   'delivered_by_id': [('parent_id', '=', own_company_add.id)]},
                        'value': {'partner_shipping_id': False, 'delivered_by_id': False}}
            # Delivery to Courier
            if self.waybill_type == 'courier':
                return {'domain': {'partner_shipping_id': [('supplier', '!=', True), ('is_courier', '!=', True)],
                                   'delivered_by_id': [('is_courier', '=', True)]},
                        'value': {'partner_shipping_id': False, 'delivered_by_id': False}}
            # Drop Shipment to Project
            if self.waybill_type == 'dropship':
                return {'domain': {'partner_shipping_id': [('is_courier', '!=', True)],
                                   'delivered_by_id': [('is_courier', '=', True)]},
                        'value': {'partner_shipping_id': False, 'delivered_by_id': False}}
                # return {'domain': {'partner_shipping_id': [('supplier', '!=', True), ('is_courier', '!=', True)], 'delivered_by_id': [('is_courier', '=', True)]},'value': {'partner_shipping_id': False, 'delivered_by_id': False}}
            # Return
            if self.waybill_type == 'return_w':
                return {'domain': {'partner_shipping_id': [('supplier', '!=', True), ('is_courier', '!=', True)],
                                   'delivered_by_id': [('supplier', '!=', True), ('is_company', '!=', True)]},
                        'value': {'partner_shipping_id': False, 'delivered_by_id': False}}
        return {}

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('way.bill') or _('New')

        return super(WayBillsModel, self).create(vals)


class WayBillLinesModel(models.Model):
    _name = 'way.bill.lines'
    _description = 'KNC Waybill Lines'
    _order = 'sequence'

    bill_id = fields.Many2one('way.bill', string='Waybill #')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', related="product_id.product_tmpl_id",
                                      string='Product Template', required=True)
    qty_on_hand = fields.Float(related='product_id.qty_available', string='Stock')
    name = fields.Char(string='Description', required=True)  # Attribute Description
    # desc = fields.Text(related='product_id.desc_attribute', string ='Attributes Description')

    qty = fields.Float(string='QTY', required=True)
    note = fields.Text(string='Product Notes')
    ref = fields.Text(string='Label Reference')
    chk = fields.Boolean(string='Line Chk')
    chk_trf = fields.Boolean(string='Xfer Chk')
    lot_id = fields.Many2many('stock.production.lot', string='LOT / Serial Number')

    sequence = fields.Integer(string='Sequence')
    section_id = fields.Many2one('sale.layout_category', string='Related Section')
    # product_uom_id = fields.Many2one('product.uom', string='UOM')
    project_id = fields.Many2one('project.project', string='Related Project', related='bill_id.project_id')
    order_id = fields.Many2one('sale.order', string='Related Sales Order', related='bill_id.order_id')
    filter_on_so = fields.Boolean(string='Filter on SO')
    active = fields.Boolean(related='bill_id.active', store=True)
    company_id = fields.Many2one('res.company', 'Company', related='bill_id.company_id')

    product_state = fields.Selection(related='product_id.activity_state', readonly=True, string='Status',
        help="DFT - DRAFT - Just Added - Data Not Checked \n"
          "AVL - AVAILABLE - Checked & Confirmed Basic Data of the Product \n"
          "REV - REVIEW - Need to Review Technical Features & Values\n"
          "CKD - CHECKED - Checked & Confirmed Technical Features of the Product \n"
          "OBS - OBSOLETE - Version no Longer Produced / Replacement Available \n"
          "EOL - END OF LIFE - Product & Versions Reached the End of its Useful Life \n")

    state = fields.Selection(
        string='Waybill State', default='draft', copy=False, related='bill_id.state', readonly=False)

    date_waybill = fields.Datetime(related='bill_id.waybill_date', store=True, string='Waybill Date')
    waybill_partner_id = fields.Many2one(related='bill_id.partner_id', store=True, string='Customer')
    waybill_ref = fields.Char(related='bill_id.note_ref', string='Waybill Reference')
    product_ref = fields.Char(related='product_id.default_code', string='Internal Reference')
    actual_qty = fields.Float(related="product_id.qty_available", readonly=True, string="Actual Qty")

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name_get()[0][1]
            if self.product_id.description_sale:
                name += '\n' + self.product_id.description_sale
            self.name = name
            # self.product_uom_id = self.product_id.uom_id

    @api.onchange('filter_on_so')
    def onchange_filter_on_so(self):
        if self.filter_on_so:
            products = self.bill_id.order_id.order_line.mapped('product_id')
            if self.filter_on_so:
                return {'domain': {'product_id': [('id', 'in', products.ids)]}, 'value': {'partner_shipping_id': False}}
        return {}


class ResPartnerBillWay(models.Model):
    _inherit = 'res.partner'

    is_courier = fields.Boolean(string="IsCourier", default=False)
    fax = fields.Char('Fax')


class SaleOrderBillWay(models.Model):
    _inherit = 'sale.order'

    new_project_id = fields.Many2one('project.project', tracking=True)


class SaleLayoutCategory(models.Model):
    _name = 'sale.layout_category'
    _description = 'sale.layout_category Description'

    so_id = fields.Many2one('sale.order', string='Sale Order')


class StockPickingWill(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.project')
