# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

from openerp import models, fields


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    description = fields.Text(

    )
