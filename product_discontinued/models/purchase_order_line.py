# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discontinued = fields.Boolean(
        related="product_id.product_tmpl_id.discontinued"
    )
