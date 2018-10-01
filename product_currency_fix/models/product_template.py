# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models, fields
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
            # si el quant cost esta en cero es critico, le pongo el costo
            # esto no debiera pasar, encima hay que hacerlo con sudo.
            pass
            #if not quant.cost or not quant.cost_product:
            #    pc = prod.currency_id.with_context(date=quant.in_date)
            #
            #    quant.sudo().write({
            #        'cost': pc.compute(cost, cc, round=False),
            #        'cost_product': cost
            #    })

            # actualizar los standard al precio del quant
            # TODO No es el lugar para hacer esto.
            #prod.write({
            #    'standard_price': quant.cost,
            #    'standard_product_price': quant.cost_product
            #})
        else:
            pc = prod.currency_id
            # no hay quants le pongo al standard el costo de hoy
            prod.write({
                'standard_price': pc.compute(cost, cc, round=False),
                'standard_product_price': cost
            })
