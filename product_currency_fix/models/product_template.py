# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import models, fields
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_product_price = fields.Float(
        digits_compute=dp.get_precision('Product Price'),
        groups="base.group_user",
        string="Product Cost",
        help="Historic cost of the product in Product currency."
    )

    def fix_quant_data(self, quant, prod, cost):

        cc = prod.company_id.currency_id
        if quant:
            # TODO QUITAR ESTO, no puedo poner costo actual aca
            pass
        else:
            pc = prod.currency_id
            # no hay quants le pongo al standard el costo de hoy
            prod.write({
                'standard_price': pc.compute(cost, cc, round=False),
                'standard_product_price': cost
            })
