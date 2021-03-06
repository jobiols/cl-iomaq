# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root
from openerp import api, fields, models
from openerp.tools import float_compare

enabled = 'avoid_selling_no_stock.group_sell_negative_stock_users'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_available = fields.Boolean(
        compute="_compute_is_available",
        readonly=True,
        default=True,
    )

    @api.multi
    def action_confirm(self):
        """ Esto atrapa los botones action_confirm y action_confirm_send
        """
        # TODO Deberia desaparecer los botones en lugar de hacer esto.
        for order in self:
            if order.is_available or self.env.user.has_group(enabled):
                super(SaleOrder, self).action_confirm()

    @api.onchange('order_line')
    def _compute_is_available(self):
        for so in self:
            is_available = True

            if self.env.user.has_group(enabled):
                so.is_available = is_available
                return

            if so.state in ['draft', 'sent']:
                for sol in self.order_line:
                    if not sol.is_available:
                        is_available = False
            so.is_available = is_available


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_available = fields.Boolean(
        compute="_compute_is_available",
        readonly=True,
        default=True,
    )

    @api.multi
    def _compute_is_available(self):
        for sol in self:
            if sol.product_id.type == 'product' and \
                    sol.order_id.state in ['draft', 'sent']:
                precision = self.env['decimal.precision'].precision_get(
                    'Product Unit of Measure')
                product_qty = self.env['product.uom']._compute_qty_obj(
                    sol.product_uom,
                    sol.product_uom_qty,
                    sol.product_id.uom_id)
                sol.is_available = True
                if float_compare(sol.product_id.virtual_available,
                                 product_qty,
                                 precision_digits=precision) == -1:
                    is_available = sol._check_routing()
                    sol.is_available = is_available
