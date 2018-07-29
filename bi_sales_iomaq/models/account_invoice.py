# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division
from openerp import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    vendor_id = fields.Many2one(
        'res.partner',
        help="The vendor who sell us this product"
    )


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    tag = fields.Char(
        string='Tags',
        compute="_compute_tag",
        readonly=True,
        store=True,
        help="This is the first tag found in the partner, it adds a Tags field"
             "in the account.invoice model in order to filter invoices and"
             "to use it as a new dimension in pivot tables"
    )

    @api.multi
    @api.depends('partner_id.category_id')
    def _compute_tag(self):
        for invoice in self:
            if invoice.partner_id and invoice.partner_id.category_id:
                invoice.tag = invoice.partner_id.category_id[0].name
