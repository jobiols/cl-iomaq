# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root
from openerp import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def update_date_prices_and_validity(self):
        self.date_order = fields.Datetime.now()
        self.onchange_company()
        return True
