# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _
from openerp.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # incremento o decremento de precio para mercadolibre, debe aparecer solo
    # con el grupo pulus_ml y si la venta esta en el team_id Mercadolibre
    price_unit_ml = fields.Float(
        help="Campo para modificar el precio unitario en productos de ML"
    )
    ml = fields.Char(
        related='order_id.team_id.name',
        help="Campo tecnico para ocultar o mostrar el campo price_unit_ml"
    )

    # we add this fields instead of making original readonly because we need
    # on change to change values, we make readonly in view because sometimes
    # we want them to be writeable
    price_unit_readonly = fields.Float(
        related='price_unit',
    )
    tax_id_readonly = fields.Many2many(
        related='tax_id',
    )
    product_can_modify_prices = fields.Boolean(
        related='product_id.can_modify_prices',
        readonly=True,
        string='Product Can modify prices')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id',
                 'price_unit_ml')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line teniendo en cuenta el campo
        price_unit_ml.
        """
        for line in self:
            unit_price = line.price_unit + line.price_unit_ml
            price = unit_price * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id,
                                            line.product_uom_qty,
                                            product=line.product_id,
                                            partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('price_unit_readonly')
    def onchange_price_unit_readonly(self):
        self.price_unit = self.price_unit_readonly

    @api.onchange('tax_id_readonly')
    def onchange_tax_id_readonly(self):
        self.tax_id = self.tax_id_readonly

    @api.multi
    @api.constrains('discount', 'product_id',
                    # this is a related none stored field
                    # 'product_can_modify_prices'
                    )
    def check_discount(self):
        for reg in self:
            if (reg.user_has_groups(
                'price_security.group_restrict_prices'
            ) and not reg.product_can_modify_prices):
                reg.env.user.check_discount(reg.discount,
                                            reg.order_id.pricelist_id.id,
                                            so_line=reg)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.constrains('pricelist_id', 'payment_term_id', 'partner_id')
    def check_priority(self):
        for reg in self:
            if not reg.user_has_groups('price_security.group_restrict_prices'):
                return True
            if (
                        reg.partner_id.property_product_pricelist and
                        reg.pricelist_id and
                        reg.partner_id.property_product_pricelist.sequence <
                        reg.pricelist_id.sequence):
                raise UserError(_(
                    'Selected pricelist priority can not be higher than '
                    'pircelist configured on partner'
                ))
            if (
                        reg.partner_id.property_payment_term_id and
                        reg.payment_term_id and
                        reg.partner_id.property_payment_term_id.sequence <
                        reg.payment_term_id.sequence):
                raise UserError(_(
                    'Selected payment term priority can not be higher than '
                    'payment term configured on partner'
                ))

    @api.onchange('partner_id')
    def check_partner_pricelist_change(self):
        pricelist = self.partner_id.property_product_pricelist
        if self.order_line and pricelist != self._origin.pricelist_id:
            self.partner_id = self._origin.partner_id
            return {'warning':
                        {"title": "Warning",
                         "message": "You can"
                                    " not change partner if there are sale "
                                    "lines and pricelist is going to be "
                                    "changed"}}
