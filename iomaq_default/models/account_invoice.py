# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api
from openerp.addons.decimal_precision import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    tag = fields.Char(
        string='Tags',
        compute="_get_tag",
        readonly=True,
        store=True
    )

    @api.one
    @api.depends('partner_id.category_id')
    def _get_tag(self):
        if self.partner_id:
            if self .partner_id.category_id:
                self.tag = self.partner_id.category_id[0].name


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    cost_unit = fields.Float(
        string='Unit Cost',
        compute="_compute_cost_unit",
        store=True,
        digits=dp.get_precision('Product Price')
    )

    @api.one
    @api.depends('product_id.standard_price', 'invoice_id.currency_id')
    def _compute_cost_unit(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None

        cost = self.product_id.standard_price

        self.cost_unit = cost
