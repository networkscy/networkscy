from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def update_description_order_line(self):
        rec = self.env['sale.order.wizard'].search([('sale_order_id', '=', self.id)])
        if rec and len(rec) > 0:
            rec = rec[0]
        else:
            rec = self.env['sale.order.wizard'].create({'sale_order_id': self.id})
        return {
            'name': _("Confirmation?"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.wizard',
            'res_id': rec.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_sale_order_line_multiline_description_sale(self, product_id):
        return self.product_id._compute_ic_custom_description(product_id=product_id)

    @api.onchange('product_id')
    def _compute_description(self):
        if self.product_id:
            self.update({'name': self.get_sale_order_line_multiline_description_sale(product_id=self.product_id)})


# Wizard for confirmation
class SaleOrderLineDescConfirmWizard(models.TransientModel):
    _name = 'sale.order.wizard'

    yes_no = fields.Char(default='Do you want to proceed for updation description?')
    sale_order_id = fields.Many2one('sale.order', string="Related Product")

    def yes(self):
        order_lines = self.env['sale.order.line'].search([('order_id', '=', self.sale_order_id.id)])
        for line in order_lines:
            line._compute_description()
        return True

    def no(self):
        return False