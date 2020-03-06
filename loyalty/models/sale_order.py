# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root


from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):

        frm_cur = self.env.user.company_id.currency_id
        to_cur = pricelist.currency_id
        purchase_price = product.standard_price
        if product_uom != product.uom_id:
            purchase_price = self.env['product.uom']._compute_price(
                product.uom_id.id, purchase_price, to_uom_id=product_uom.id)
        ctx = self.env.context.copy()
        ctx['date'] = date
        price = frm_cur.with_context(ctx).compute(
            purchase_price, to_cur, round=False)
        return {'purchase_price': price}
