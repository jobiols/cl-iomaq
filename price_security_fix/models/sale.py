# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # por alguna razon que no entiendo esto solo funciona si la funcion
    # check_discount se llama de otra forma que no sea check_discount

    @api.multi
    @api.constrains('discount', 'product_id',
                    # this is a related none stored field
                    # 'product_can_modify_prices'
                    )
    def check_discount_sale(self):
        for reg in self:
            if (reg.user_has_groups('price_security.group_restrict_prices'
                                    ) and not reg.product_can_modify_prices):
                reg.env.user.check_discount(reg.discount,
                                            reg.order_id.pricelist_id.id)
