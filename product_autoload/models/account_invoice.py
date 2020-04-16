# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import api, models, fields
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    invoice_discount = fields.Float(
        string='Invoice Discount',
        default=False,
        help="the discount that applied to the purchase price minus the "
             "discount line gives the actual purcahse price. If there is no"
             "global discount then it is 0%"
    )

    date_invoice = fields.Date(
        related="invoice_id.date_invoice",
        help="helper para corregir costos",
        store=True
    )


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    discount_processed = fields.Boolean(
        default=False,
        help='Shows whether this invoice was processed with invoice_discounts'
    )

    @api.multi
    def compute_invoice_discount(self):
        """ Calcula el descuento de cada linea basado en el descuento global
            que se hace con una linea de factura que representa el descuento
            Esa linea tiene precio negativo.
        """

        # obtener los impuestos de iva que buscaremos
        tax21 = self.env['account.tax'].search(
            [('amount', '=', 21.0), ('type_tax_use', '=', 'purchase')])
        tax105 = self.env['account.tax'].search(
            [('amount', '=', 10.5), ('type_tax_use', '=', 'purchase')])

        for inv in self:
            number = inv.document_number if \
                inv.document_number else inv.display_name
            _logger.info('Processing discounts on invoice %s' % number)
            # poner en cero los acumuladores
            prod_iva_21 = disc_iva_21 = prod_iva_105 = disc_iva_105 = 0

            # procesar cada linea de la factura
            for line in inv.invoice_line_ids:
                # el subtotal de la linea
                subtotal = line.price_unit * (
                    1 - line.discount / 100) * line.quantity

                # sumar IVA 21%
                if tax21 in line.invoice_line_tax_ids:
                    if line.price_subtotal_signed >= 0:
                        # sumar subtotales con el descuento de linea aplicado
                        prod_iva_21 += subtotal
                    else:
                        # sumar descuentos (no tienen producto)
                        disc_iva_21 += subtotal

                # sumar IVA 10.5%
                if tax105 in line.invoice_line_tax_ids:
                    if line.price_subtotal_signed >= 0:
                        # sumar subtotales con el descuento de linea aplicado
                        prod_iva_105 += subtotal
                    else:
                        # sumar descuentos (no tienen producto)
                        disc_iva_105 += subtotal

            disc_21 = disc_iva_21 / prod_iva_21 if prod_iva_21 else False
            disc_105 = disc_iva_105 / prod_iva_105 if prod_iva_105 else False

            # ponerle el descuento global a todas las lineas
            lines21 = inv.invoice_line_ids.filtered(
                lambda r: r.price_subtotal_signed > 0 and
                tax21 in r.invoice_line_tax_ids)
            lines21.write({'invoice_discount': disc_21})

            lines105 = inv.invoice_line_ids.filtered(
                lambda r: r.price_subtotal_signed > 0 and
                tax105 in r.invoice_line_tax_ids)
            lines105.write({'invoice_discount': disc_105})

            inv.discount_processed = True
