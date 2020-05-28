# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    discontinued = fields.Boolean(
        related="product_tmpl_id.discontinued"
    )
