# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division
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

    @api.multi
    @api.depends('partner_id.category_id')
    def _compute_tag(self):
        for invoice in self:
            if invoice.partner_id and invoice.partner_id.category_id:
                invoice.tag = invoice.partner_id.category_id[0].name


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    product_margin = fields.Float(
        string='Product Margin',
        compute="_compute_product_margin",
        store=True,
        digits=dp.get_precision('Product Price'),
        help="This is the margin between standard price and list_price"
    )
    product_iva = fields.Float(
        compute="_compute_product_iva",
        store=True,
        digits=dp.get_precision('Product Price'),
        help="This is the product iva"
    )
    sign = fields.Integer(
        compute="_compute_sign",
        store=True
    )

    @api.multi
    @api.depends('product_id.standard_price', 'invoice_id.currency_id')
    def _compute_product_margin(self):
        for ail in self:
            price = ail.product_id.list_price
            cost = ail.product_id.standard_price
            ail.product_margin = (price - cost) / price if price else 0

    @api.multi
    @api.depends('product_id.standard_price', 'invoice_id.currency_id')
    def _compute_product_iva(self):
        for ail in self:
            iva = False
            for tax in ail.product_id.taxes_id:
                iva = tax.amount
            ail.product_iva = iva / 100 if iva else 0

    @api.multi
    @api.depends('invoice_id')
    def _compute_sign(self):
        for ail in self:
            ail.sign = ail.invoice_id.type in ['in_refund',
                                               'out_refund'] and -1 or 1
