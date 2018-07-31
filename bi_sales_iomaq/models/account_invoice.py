# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division
from openerp import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    vendor_id = fields.Many2one(
        'res.partner',
        help="The vendor who sell us this product",
        compute='_compute_vendor_id',
        store=True
    )

    @api.multi
    @api.depends('product_id')
    def _compute_vendor_id(self):
        """ Tratar de obtener el vendor que me vendio este producto, esto es
            lo mejor que se puede hacer por ahora.
            Busco en stock.pack.operation la ultima vez que ingreso el producto
            y obtengo el vendor del picking_id.
        """
        # TODO ver de guardar el vendor en el quant.
        op_object = self.env['stock.pack.operation']
        for line in self:
            op = op_object.search([('product_id', '=', line.product_id.id),
                                   ('location_dest_id', '=', 12)],
                                  limit=1, order='id desc')
            line.vendor_id = op.picking_id.partner_id \
                if op.picking_id.partner_id.supplier else False
            default_code = line.product_id.default_code

            if default_code == '123.CI.38' or \
                    default_code == '200.8.400' or \
                    default_code == '380.LCM.24' or \
                    default_code == '380.LCM.8' or \
                    default_code == '381.CL.10' or \
                    default_code == '381.CL.13' or \
                    default_code == '601.MS.801C' or \
                    default_code == '601.SB.1014' or \
                    default_code == '601.MS.1001/2' or \
                    default_code == '76.4.16':
                line.vendor_id = 16

    @api.model
    def fix_vendor_id(self):
        lines = self.env['account.invoice.line'].search(
            [('invoice_id.type', '=', 'out_invoice')])
        lines._compute_vendor_id()


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
