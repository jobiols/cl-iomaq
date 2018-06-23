# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    final_price = fields.Float(
        string='Price tax included',
        compute='_compute_final_price',
        digits=dp.get_precision('Product Price'),
        help='Final Price. This is the public price with tax',
    )

    @api.multi
    def _compute_final_price(self):
        for prod in self:
            # obtener el rate con la divisa del producto
            rate = prod.currency_id.rate

            # obtener el precio de lista en moneda de la compa~nia
            lp = prod.list_price / rate if rate != 0 else 0

            # poner el precio iva incluido
            tax = prod.taxes_id[0].amount if prod.taxes_id else 100
            prod.final_price = lp * (1 + tax / 100)
