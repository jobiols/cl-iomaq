# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api
from openerp.addons.decimal_precision import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    tag = fields.Char(
        string='Tags',
        compute="_compute_tag",
        readonly=True,
        store=True,
        help="This is the first tag found in the partner"
    )

    @api.one
    @api.depends('partner_id.category_id')
    def _compute_tag(self):
        if self.partner_id:
            if self .partner_id.category_id:
                self.tag = self.partner_id.category_id[0].name


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    cost_unit = fields.Float(
        string='Unit Cost',
        compute="_compute_cost_unit",
        store=True,
        digits=dp.get_precision('Product Price'),
        help="This is the product standard price from the product translated "
             "to the company currency"
    )

    @api.one
    @api.depends('product_id.standard_price', 'invoice_id.currency_id')
    def _compute_cost_unit(self):
        for ail in self:
            # traer el tipo de cambio del producto
            rate = ail.product_id and ail.product_id.currency_id.rate or None

            # obtener el costo en moneda de la compa~nia
            cost = ail.product_id.standard_price / rate if rate != 0 else 0
            ail.cost_unit = cost
