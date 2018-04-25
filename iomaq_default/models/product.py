# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api
from openerp.addons.decimal_precision import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"

    final_price = fields.Float(
        string='Price tax included',
        compute='_get_final_price',
        digits=dp.get_precision('Product Price'),
        help='Final Price. This is the public price with tax',
    )

    @api.multi
    def _get_final_price(self):
        for prod in self:
            tax = prod.taxes_id[0].amount if prod.taxes_id else 100
            prod.final_price = prod.list_price * (1 + tax / 100)
