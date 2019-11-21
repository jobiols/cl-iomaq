# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class FakeStock(object):
    def __init__(self):
        self._stock = []

    def append(self, quant):
        self._stock.append(quant)

    def push(self, qty, price):
        """ Mete un quant con cantidad y precio
        """
        self._stock.append({'qty': qty,
                            'price': price})

    def pop(self, qty):
        """ Saca qty productos ajustndo los quants y devolviendo el precio
        """
        num = 0
        # calcular cuantos quants estan afectados, habra que quitar
        # num -1 y corregir o no el ultimo
        for quant in self._stock:
            num += 1
            if self.qty(n=num) >= qty:
                break

        # obtener la cantidad de producto que hay en los num-1 quants
        quitados = self.qty(n=num - 1)

        # mover los num-1 quants a out
        out = FakeStock()
        for x in range(0, num - 1):
            q = self._stock.pop(0)
            out.append(q)

        # obtener la cantidad de producto a corregir en el ultimo quant
        corregir = qty - quitados

        # apuntar al ultimo
        if self._stock:
            quant = self._stock[0]
        else:
            _logger.error('STOCK NEGATIVO')
            return 0

        # corregir la cantidad en este quant pero no permitir cero
        quant['qty'] -= corregir
        if quant['qty'] <= 0:
            quant['qty'] = 0

        # meter el pedazo de quant en out si es que no es cero la cantidad
        # y con el mismo precio
        if corregir:
            out.push(corregir, quant['price'])

        # en el caso de que la correccion me lleve a un quant en cero lo mato
        if quant['qty'] == 0:
            self._stock.pop(0)

        return out._price()

    def qty(self, n=-1):
        """ Devuelve la cantidad en los n quants primeros para salir si es
            False los suma todos
        """
        if n == 0:
            return 0
        qty = 0
        for e in self._stock:
            qty += e['qty']
            if n != -1:
                n -= 1
            if n >= 0 and n == 0:
                return qty
        return qty

    def _price(self, n=-1):
        """ Devuelve el promedio ponderado del precio de los n quants primeros
            para salir.
        """
        price = qty = 0
        for e in self._stock:
            price += e['price'] * e['qty']
            qty += e['qty']

            if n:
                n -= 1
            if n >= 0 and n == 0:
                return price / qty if qty else 0

        return price / qty if qty else 0


# #############################################################################


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    vendor_id = fields.Many2one(
        'res.partner',
        help="The vendor who sell us this product",
        compute='_compute_vendor_id',
        store=True
    )

    product_margin = fields.Float(
        string='Product Margin',
        help="This is the margin between standard_price and list_price taking "
             "into account line discounts, is the margin for this line only"
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
    def _compute_product_margin(self, date=False):
        for ail in self:
            if ail.product_id and ail.invoice_id.type in ['out_invoice',
                                                          'out_refund']:
                # precio de venta sacado de la linea de factura, teniendo
                # en cuenta los descuentos que pudiera haber.
                disc = ail.discount / 100
                price = ail.price_unit * (1 - disc)

                # obtener las currencies de invoice y compania.
                ic = ail.invoice_id.currency_id
                cc = ail.company_id.currency_id

                # convierte currency de ic a cc
                price = ic.compute(price, cc, round=False)

                business_mode = ail.product_id.business_mode
                # TODO
                # Esto es un parche porque en el default pusimos normal
                # hay que arreglarlo rapidamente.
                if business_mode != 'consignment':
                    # precio de costo del producto en moneda de la company
                    # es el costo del quant mas viejo
                    cost = ail.product_id.standard_price

                if business_mode == 'consignment':
                    if date:
                        # buscar el precio historico (solo para el fix)
                        pid = ail.product_id
                        cost = self.get_fix_historic_price(date, pid)
                    else:
                        # el ultimo precio que le cargamos (lo normal)
                        cost = ail.product_id.bulonfer_cost

                    # convertimos de moneda del producto a la company
                    pc = ail.product_id.currency_id
                    cost = pc.compute(cost, cc, round=False)

                if business_mode == 'undefined':
                    # falla porque no sabemos el proveedor
                    ail.product_margin = 1e10
                    return

                ail.product_margin = price / cost - 1 \
                    if cost and price else 1e10

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

    @api.multi
    @api.depends('product_id')
    def _compute_vendor_id(self):
        """ Obtener el vendor que me vendio este producto, desde los seller_ids
            del producto. Si no lo tiene busco en stock.pack.operation la
            ultima vez que ingreso el producto y obtengo el vendor del
            picking_id.
        """
        for rec in self:
            # todos los vendors de este producto
            domain = [
                ('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)]
            vendor = rec.product_id.seller_ids.search(domain,
                                                      order='date_start desc',
                                                      limit=1)
            if vendor:
                rec.vendor_id = vendor.name.id
            else:
                # no tengo vendors en el producto busco en stock la ultima vez
                # que ingreso el producto
                op_object = self.env['stock.pack.operation']
                for line in self:
                    domain = [('product_id', '=', line.product_id.id),
                              ('location_dest_id', '=', 12)]
                    op = op_object.search(domain, limit=1, order='id desc')
                    rec.vendor_id = op.picking_id.partner_id \
                        if op.picking_id.partner_id.supplier else False

    @api.model
    def fix_bulonfer_bi(self):
        for rec in self.search([]):
            # todos los vendors de este producto
            domain = [
                ('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)]
            vendor = rec.product_id.seller_ids.search(domain,
                                                      order='date_start desc',
                                                      limit=1)
            if vendor:
                rec.vendor_id = vendor.name.id
                _logger.info('product %s' % rec.product_id.name)

    @api.model
    def get_fix_historic_price(self, date, pid):
        """ Para correr a mano desde fix_compute_margin
        """
        # buscar el product_supplierinfo para este producto

        domain = ['&', ('product_tmpl_id', '=', pid.product_tmpl_id.id),
                  '|',
                  '&', ('date_start', '<=', date), ('date_end', '=', False),
                  '&', ('date_start', '<=', date), ('date_end', '>=', date)
                  ]
        ps = self.env['product.supplierinfo'].search(domain, limit=1)
        if ps:
            return ps.price
        else:
            return False

    @api.model
    def fix_compute_margin(self):
        """ Para correr a mano recalcula product margin. a los productos que
            tienen proveedor con marca de consignacion
        """

        # me traigo todas las ail que corresponden a productos en consignacion
        cr = self._cr
        cr.execute("""
            SELECT ail.id from account_invoice_line ail
              JOIN product_product pp
              ON ail.product_id = pp.id
              JOIN product_supplierinfo ps
              ON ps.product_tmpl_id = pp.product_tmpl_id
              JOIN res_partner rp
              on rp.id = ps.name
            WHERE rp.business_mode = 'consignment';
        """)

        tuples = cr.fetchall()
        ids = [i[0] for i in tuples]

        ail_obj = self.env['account.invoice.line']
        ails = ail_obj.browse(ids)
        for ail in ails:
            ail._compute_product_margin(date=ail.invoice_id.date_invoice)
            _logger.info('Fixing %s on %s' % (ail.product_id.default_code,
                                              ail.date_invoice))


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    tag = fields.Char(
        string='Tags',
        compute="_compute_tag",
        readonly=True,
        store=True,
        help="This is the first tag found in the partner, it adds a Tags "
             "field in the account.invoice model in order to filter invoices "
             "and to use it as a new dimension in pivot tables"
    )

    @api.multi
    @api.depends('partner_id.category_id')
    def _compute_tag(self):
        for invoice in self:
            if invoice.partner_id and invoice.partner_id.category_id:
                invoice.tag = invoice.partner_id.category_id[0].name

    @api.multi
    def write(self, vals):
        for inv in self:
            for line in inv.invoice_line_ids:
                line._compute_product_margin()

        return super(AccountInvoice, self).write(vals)
