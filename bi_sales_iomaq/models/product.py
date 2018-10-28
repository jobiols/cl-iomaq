# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api
import logging
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        'bi_sales_iomaq.brand',
        string='Brand',
        help='Brand of the product',
        store=True,
    )

    final_price = fields.Float(
        string='Price tax included',
        compute='_compute_final_price',
        digits=dp.get_precision('Product Price'),
        help='Final Price. This is the public price with tax',
    )

    @api.multi
    def _compute_final_price(self):
        for prod in self:
            cc = prod.company_id.currency_id
            pc = prod.currency_id

            # obtener el precio de lista en moneda de la compa~nia
            lp = pc.compute(prod.list_price, cc, round=False)

            # poner el precio iva incluido
            tax = prod.taxes_id[0].amount if prod.taxes_id else 0
            prod.final_price = lp * (1 + tax / 100)

    @api.model
    def fix_historic_cost(self):
        """ Corrige costos de los quants en STIHL
            recorre todos los productos con currency USD

            pone standard price y los quants
            Para correr a mano
        """

        ail_obj = self.env['account.invoice.line']
        ails = ail_obj.search(
            [('product_id.default_code', 'not like', '-STIHL'),
             ('invoice_id.type', '=', 'out_invoice')],
            order='id')

        for ail in ails:
            tmpl = ail.product_id.product_tmpl_id
            invoice_line = tmpl.closest_invoice_line(
                tmpl, ail.invoice_id.date_invoice)

            invoice_price = 0
            if invoice_line and invoice_line.price_unit:
                # precio que cargaron en la factura de compra
                invoice_price = invoice_line.price_unit
                # descuento en la linea de factura
                invoice_price *= (1 - invoice_line.discount / 100)
                # descuento global en la factura
                invoice_price *= (1 + invoice_line.invoice_discount)

                if invoice_line.invoice_id.partner_id.ref == 'BULONFER':
                    # descuento por nota de credito al final del mes esto
                    # vale solo para bulonfer
                    invoice_price *= (1 - 0.05)

                standard_price = invoice_price
                standard_product_price = invoice_price

                # recalcular el margen del producto
                if ail.product_id.standard_price > standard_price:
                    ail.product_id.standard_price = standard_price
                    ail.product_id.standard_product_price = \
                        standard_product_price

                _logger.info('product like %s' % tmpl.default_code)
