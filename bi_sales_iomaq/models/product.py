# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        'bi_sales_iomaq.brand',
        string='Brand',
        help='Brand of the product',
    )
