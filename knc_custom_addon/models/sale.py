# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp



# class SaleClass(models.Model):
    # _name = "sale.class"

    # name = fields.Char()

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    
    
    # def _total_discount(self):
        # for rec in self:
            # discount_amount = main_unit_price = main_unit_price2 = 0
            # for line in rec.order_line:
                # discount_amount += line.discount_amount
                # main_unit_price2 += line.price_unit * line.product_uom_qty
                # main_unit_price += line.price_unit * line.product_uom_qty
            # rec.discount_amount = discount_amount
            # rec.total_before_discount = main_unit_price
            # rec.avg_discount = (discount_amount*100)/main_unit_price2 if main_unit_price2 else 0

    # @api.depends('amount_untaxed','amount_after_discount')
    # def _discount_amount_global(self):
    #     for rec in self:
    #         rec.discount_amount_global = -(rec.amount_untaxed - rec.amount_after_discount)
    #     return


    # @api.depends('order_line.extra_cost_amount','order_line.product_uom_qty','order_line.real_cost_amount','order_line.purchase_price')
    # def _extra_cost(self):
        # for order in self:
            # extra_cost = real_cost_amount = total_real_cost_amount = total_cost = 0
            # for line in order.order_line:
                # if line.state != 'cancel':
                # extra_cost += line.extra_cost_amount * line.product_uom_qty
                # real_cost_amount += line.real_cost_amount
                # total_real_cost_amount += line.real_cost_amount * line.product_uom_qty
                # total_cost += line.purchase_price * line.product_uom_qty
            # order.extra_cost = extra_cost
            # order.real_cost_amount = real_cost_amount
            # order.total_real_cost_amount = total_real_cost_amount 
            # order.extra_cost_per = ((order.extra_cost / total_cost)*100) if total_cost else 0
            # total_amount = order.amount_after_discount if order.apply_discount else order.amount_untaxed
            # total_amount = order.amount_untaxed
            # real_margin = total_amount - order.total_real_cost_amount
            # order.real_margin = real_margin
            # order.real_margin_per = (real_margin * 100)/total_amount if total_amount else 100


    contact_id = fields.Many2one('res.partner',"Contact Person")
    print_discount = fields.Boolean('Print Discount')
    print_taxes = fields.Boolean('Print VAT')
    print_total = fields.Boolean('Print Total')
    client_order_ref = fields.Char(string='Customer Reference', copy=True)
    new_project_id = fields.Many2one('project.project', 'Project')
    # total_before_discount = fields.Monetary('Subtotal Before Discounts', help="Subtotal Before Discounts - Original Value of Goods", compute="_total_discount", digits=dp.get_precision('Discount'))
    # discount_amount = fields.Float('Discount Amount on Line Items', compute="_total_discount", digits=dp.get_precision('Discount'))
    # avg_discount = fields.Float('Avg Discount on Line Items', help="Average Discount % on Line Items", compute="_total_discount", digits=dp.get_precision('Discount'))
    # print_avg_discount = fields.Boolean()
    # discount_amount_global = fields.Float("Discount Amount on Total Price",compute='_discount_amount_global', help="Total Discount on Total Amount")
    title = fields.Char("Title")
    # service_report = fields.Char("Service Report")
    # invoice_no = fields.Char("Invoice Number")
    sale_class_id = fields.Many2one('sale.class', "Sale Type")
    # total_cost = fields.Monetary(string="Total Purchase Cost", compute='_product_cost', help="toal cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # extra_cost_per = fields.Float(string="Avg Extra Cost %", compute='_extra_cost', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # extra_cost = fields.Monetary(string="Total Extra Cost", compute='_extra_cost', help="It gives profitability by calculating the difference between the Unit Price and the cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # real_margin = fields.Monetary(string="Total Profit", compute='_extra_cost', help="It gives profitability by calculating the difference between the Unit Price and the real cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # real_margin_per = fields.Float(string="Gross Margin", compute='_extra_cost', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # real_cost_amount = fields.Monetary(string="Real Cost", compute="_extra_cost", readonly=True, currency_field='currency_id', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # total_real_cost_amount = fields.Monetary(string="Total Real Cost", compute="_extra_cost", readonly=True, currency_field='currency_id', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    # total_cost = fields.Monetary(string="Total Purchase Cost", compute='_product_cost', help="toal cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'), track_visibility='onchange')
    image_size = fields.Selection(
            [('image', 'Large Image'), ('image_medium', 'Medium Image'),
             ('image_small', 'Small Image')],
                'Line Image Size', default="image_medium", help="Select the Product [Image] Size to be printed")
    approved_by = fields.Boolean('Approved By')
    only_bom = fields.Boolean('Only Print BOM')
    
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals["title"] = self.title
        return invoice_vals
    
    


    # @api.onchange('new_project_id')
    # def oncnagne_new_project_id(self):
        # if self.new_project_id:
            # self.project_id = self.new_project_id.analytic_account_id.id
        # else:
            # self.project_id = False

    # def print_quotation(self):
        # self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        # return self.env['report'].get_action(self, 'acs_networkscy_extension.report_saleorder')

    #def report_saleorder_document(self):
     #   for rec in self 
      #      rec.new_state = 'quotation_sent'
  
    # def print_report_quotation(self):
        # self.filtered(lambda s: s.new_state == 'quotation').write({'new_state': 'quotation_sent'})
        # return self.env.ref('acs_networkscy_extension.report_saleorder_document').report_action(self)

    # def toapproved(self):
        # self.filtered(lambda s: s.new_state == 'quotation').write({'new_state': 'approved'})
        # self.filtered(lambda s: s.new_state == 'quotation_sent').write({'new_state': 'approved'})

    # def tolost(self):
        # self.filtered(lambda s: s.new_state == 'quotation').write({'new_state': 'lost'})
        # self.filtered(lambda s: s.new_state == 'quotation_sent').write({'new_state': 'lost'})

   # def action_confirm(self):
    #    self.write({'new_state': 'sale_order'})
        

    # def _product_cost(self):
        # for order in self:
            # total_cost = 0
            # for line in order.order_line:
                # if line.state != 'cancel':
                # total_cost += line.purchase_price * line.product_uom_qty
            # order.total_cost = total_cost



    # new status bar 
    # new_state = fields.Selection([
        # ('quotation', 'Quotation'),
        # ('quotation_sent', 'Quotation Sent'),
        # ('approved', 'Approved'),
        # ('need_invoice', 'Need Invoice'),
        # ('need_delivery', 'Need Delivery'),
        # ('lost', 'Lost'),
        # ('locked', 'Locked')
        # ],default='quotation', track_visibility='always')

    # if ("new_state" == "sale_order" and "invoice_no" == ''):
       # self.write({'new_state': 'need_invoiced'})


    # def website_confirm_order(self):
       # self.write({'new_state': 'quotation_sent'})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    show_details = fields.Boolean(string="Show details", default=True)
    show_subtotal = fields.Boolean(string="Show subtotal", default=False)

    # @api.depends('discount','price_unit','product_uom_qty')
    # def _total_discount(self):
        # for rec in self:
            # discount = ((rec.discount*rec.price_unit)/100)
            # rec.discount_per_unit = -(discount)
            # rec.discount_amount = -(discount*rec.product_uom_qty)
            # rec.discounted_unit_price = rec.price_unit - discount
            # rec.price_without_discount = rec.price_unit * rec.product_uom_qty

    # @api.onchange('product_id')
    # def product_id_change(self):
        # res = super(SaleOrderLine,self).product_id_change()
        # extra_cost = 0.0
        # if self.product_id:
            # extra_cost = self.product_id.categ_id.extra_cost
            # self.extra_cost = str(round(extra_cost,2)) + u"\u00A0"
            # print (" self.extra_cost 000", self.extra_cost)
        # return res

    # @api.depends('discounted_unit_price','real_cost_amount')
    # def _profit_amount(self):
        # for rec in self:
            # rec.profit_amount = rec.discounted_unit_price - rec.real_cost_amount

    # discount_amount = fields.Float('Discount Amount', compute="_total_discount", digits=('Discount'))
    # discount_per_unit = fields.Float('Discount Per Unit', compute="_total_discount", digits=('Discount'))
    # discounted_unit_price = fields.Float('Disc Price', compute="_total_discount", digits=('Discount'))
    # price_without_discount = fields.Monetary('Price', compute="_total_discount", digits=('Discount'))
    # extra_cost = fields.Float("Ext Cost(%)",digits=('Product Price'))
    # extra_cost_amount = fields.Float(compute="_real_cost_amount", readonly=True, string="Extra Cost", digits=('Product Price'))
    # real_cost_amount = fields.Float(compute="_real_cost_amount", readonly=True, string="Total Cost", digits=('Product Price'))
    # margin_percentage = fields.Char(compute='_get_total_percentage', string='Markup %')
    # new_margin_percentage = fields.Char(string='Margin %', compute='_get_total_percentage')
    # qty_available = fields.Float(related='product_id.qty_available', string='AVL')
    # profit_amount = fields.Float(compute="_profit_amount", readonly=True, string="Unit Profit", digits=dp.get_precision('Product Price'))

    
    # @api.depends('purchase_price', 'extra_cost')
    # def _real_cost_amount(self):
        # for rec in self:
            # extra_cost_amount = (rec.purchase_price * rec.product_id.categ_id.extra_cost)/100
            # rec.extra_cost_amount = extra_cost_amount
            # rec.real_cost_amount = extra_cost_amount + rec.purchase_price


    # @api.depends('price_unit','product_uom_qty', 'discount','real_cost_amount')
    # def _get_total_percentage(self):
        # sale_price = discount = cost = margin_amount  = new_margin_percentage = 0.0
        # for record in self:
            # if record.product_id:
                # sale_price = record.price_unit * record.product_uom_qty
                # discount = (sale_price*record.discount)/100
                # cost = record.real_cost_amount * record.product_uom_qty
                # margin_amount = (sale_price - discount) - cost
                # if record.profit_amount and record.purchase_price > 0.0:
                    # new_margin_percentage = (record.profit_amount / record.purchase_price) * 100 
                # else:
                    # new_margin_percentage = 100
                # record.margin_percentage = str(round(margin_percentage,2)) + u"\u00A0" + '%'
            # record.new_margin_percentage = str(round(new_margin_percentage,2)) + u"\u00A0" + '%'


# class ProductCategory(models.Model):
    # _inherit = "product.category"

    # extra_cost = fields.Float("Break even % markup to cover company cost", digits=('Product Price'))
    
# class LandedCost(models.Model):
    # _inherit = "stock.landed.cost"
    
    # landedcosttitle = fields.Char("Purchase Order")
    
    
    