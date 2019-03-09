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
    def _compute_product_margin(self):
        for ail in self:
            if ail.product_id and ail.invoice_id.type in ['out_invoice','out_refund']:
                # precio de venta sacado de la linea de factura, teniendo
                # en cuenta los descuentos que pudiera haber.
                disc = ail.discount / 100
                price = ail.price_unit * (1 - disc)

                # obtener las currencies de invoice y compania.
                ic = ail.invoice_id.currency_id
                cc = ail.company_id.currency_id

                # convierte currency de ic a cc
                price = ic.compute(price, cc, round=False)

                # precio de costo sacado del producto en moneda de la company
                cost = ail.product_id.standard_price

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

    """
    @api.model
    def fix_recalculate_invoice_discount(self):
        "" " Fuerza el recalculo de invoice discounts.
        "" "
        _logger.info('fix_recalculate_invoice_discount')

        ai_obj = self.env['account.invoice']
        ais = ai_obj.search([])
        ais.write({'discount_processed': False})

    @api.model
    def fix_996(self):
        "" " Para correr a mano, corrije el margen de ail de los productos 996
            basado en standard_price y list_price de la ficha del producto.
            Ademas corrije el costo historico.
            Sabemos que los precios estan en ARS asi que no tenemos en cuenta
            multimoneda
        "" "
        product_obj = self.env['product.template']
        products = product_obj.search([('default_code', '=like', '996%')])
        for product in products:
            cost = product.standard_product_price
            product.standard_price = cost

            # corregir costo en stock
            for history in product.cost_history_ids:
                history.cost = cost
                history.cost_product = cost
                _logger.info('Fixing %s on %s' % (product.default_code, cost))

        ail_obj = self.env['account.invoice.line']
        # seleccionar productos 996, que sean facturas de venta
        # ordenar la lista por producto y luego por fecha
        ails = ail_obj.search([('product_id.default_code', '=like', '996.%'),
                               ('invoice_id.type', '=', 'out_invoice')],
                              order="product_id,date_invoice")

        for ail in ails:
            cost = ail.product_id.standard_product_price
            ail.product_id.standard_price = cost
            ail._compute_product_margin()
            _logger.info('Fixing %s on %s' % (
                ail.product_id.default_code,
                ail.product_id.list_price / cost - 1))

    @api.model
    def fix_product_historic(self, data):
        "" " Para correr a mano, corrije el costo historico del producto
            basado en standard_product_price y list_price de la ficha del
            producto. no tiene en cuenta multimoneda.
            regenera el product_margin
        "" "

        product_obj = self.env['product.template']
        products = product_obj.search([('default_code', 'in', data)])
        for product in products:
            cost = product.standard_product_price
            product.standard_price = cost

            # corregir costo en stock
            for history in product.cost_history_ids:
                history.cost = cost
                history.cost_product = cost
                _logger.info('Fixing %s on %s' % (product.default_code, cost))

        ail_obj = self.env['account.invoice.line']
        # seleccionar que sean facturas de venta
        # ordenar la lista por producto y luego por fecha
        ails = ail_obj.search([('product_id.default_code', 'in', data),
                               ('invoice_id.type', '=', 'out_invoice')],
                              order="product_id,date_invoice")

        for ail in ails:
            cost = ail.product_id.standard_product_price
            ail.product_id.standard_price = cost
            ail._compute_product_margin()
            _logger.info('Fixing %s on %s' % (
                ail.product_id.default_code,
                ail.product_id.list_price / cost - 1))

    @api.model
    def fix_supplierinfo_currency(self):
        "" " para correr a mano arregla el currency en supplierinfo
        "" "
        supp_info_obj = self.env['product.supplierinfo']
        for info in supp_info_obj.search([]):
            curr = info.product_tmpl_id.currency_id
            if info.currency_id != curr:
                info.currency_id = curr
                _logger.info('Fixing currency %s' %
                             info.product_tmpl_id.default_code)

    @api.model
    def fix_simule_sale(self, products):
        "" " Pone el precio del quant mas viejo en standard_price y product_
            standard_price como si se vendiera el producto
        "" "
        _logger.info('fix_simule_sale %s' % products)

        domain = [('virtual_available', '!=', 0)]
        if products:
            domain += [('default_code', 'in', products)]

        product_obj = self.env['product.template']

        for prod in product_obj.search(domain):
            quant = product_obj.oldest_quant(prod)
            prod.standard_price = quant.cost
            prod.standard_product_price = quant.cost_product
            _logger.info('fix_prod %s' % prod.default_code)

    @api.model
    def fix_recalculate_invoice_cost(self, products):
        domain = []
        if products:
            domain += [('default_code', 'in', products)]

        product_obj = self.env['product.template']
        product_obj.search(domain).set_invoice_cost()

    @api.model
    def fix_no_hay_stock(self, products):
        "" " Si el producto no tiene stock entonces pongo
            el costo hoy en standard_cost y standard_product_cost.
        "" "
        _logger.info('fix_no_hay_stock %s' % products)

        prod_obj = self.env['product.template']
        domain = [('virtual_available', '=', 0)]

        if products:
            domain += [('default_code', 'in', products)]

        for prod in prod_obj.search(domain):
            pc = prod.currency_id
            cc = prod.company_id.currency_id
            diff = prod.standard_price - pc.compute(prod.bulonfer_cost, cc) + \
                   prod.standard_product_price - prod.bulonfer_cost
            if diff > 1:
                _logger.info('ZERO STOCK Fixing %s' % (prod.default_code))

                prod.standard_price = pc.compute(prod.bulonfer_cost, cc)
                prod.standard_product_price = prod.bulonfer_cost

    @api.model
    def fix_product_margin(self, products):
        "" " Corrije el margen de un producto teniendo en cuenta las facturas
            de compra y venta y usando un fake stock para calcular el margen
            real. No toca el historic.

            Si no hay facturas de compra toma el precio standard.
        "" "

        self.fix_recalculate_invoice_cost(products)

        # por las dudas aunque ya deberia estar corregido
        self.fix_no_hay_stock(products)

        new_prod = False
        _logger.info('fix_product_margin %s' % products)

        if products:
            domain = [('product_id.default_code', 'in', products)]
        else:
            domain = []

        ail_obj = self.env['account.invoice.line']
        # ordenar la lista por producto y luego por fecha
        ails = ail_obj.search(domain, order="product_id,date_invoice")

        cost = 0
        for ail in ails:
            # Si cambia el producto recrear el fake stock
            if new_prod != ail.product_id:
                new_prod = ail.product_id
                _stock = FakeStock()
                cost = 0

            _logger.info('Fixing %s on %s' % (
                ail.product_id.default_code, ail.date_invoice))

            cc = ail.company_id.currency_id
            # busco facturas de compra
            if ail.invoice_id.type == 'in_invoice':
                # acumulo stock
                # descuento de linea
                ldisc = (1 - ail.discount / 100)
                # descuento global
                idisc = (1 + ail.invoice_discount)

                cost = ail.price_unit * ldisc * idisc
                ic = ail.currency_id.with_context(date=ail.date_invoice)
                # lo pasamos del ic al cc
                cost = ic.compute(cost, cc)
                _stock.push(ail.quantity, cost)

            # busco facturas de venta o reembolso
            if ail.invoice_id.type == 'out_refund':
                # bajo el stock
                _stock.pop(ail.quantity)
                ail.product_margin = 0

            if ail.invoice_id.type == 'out_invoice':
                # bajo el stock, si hay errores de stock negativo intento
                # ponerle el ultimo precio que tengo.
                the_cost = _stock.pop(ail.quantity)
                if not the_cost:
                    the_cost = cost
                    # si el cost es cero es porque no encontro facturas de
                    # compra, entonces tomo el standard product price
                    if not cost:
                        the_cost = ail.product_id.standard_product_price

                # tengo en cuenta el tipo de cambio del dia de la factura
                pc = ail.product_id.currency_id
                cc = ail.company_id.currency_id.with_context(
                    date=ail.date_invoice)

                ail.product_id.standard_price = the_cost
                ail.product_id.standard_product_price = cc.compute(the_cost,
                                                                   pc)
                ail._compute_product_margin()
            else:
                # in_invoice, in_refund
                ail.product_margin = 0

        # esto para que vuelva a tomar el primer quant como costo.
        self.fix_simule_sale(products)
    """

    @api.model
    def fix_compute_margin(self):
        """ Para correr a mano recalcula product margin. a los que le falta
        """
        ail_obj = self.env['account.invoice.line']
        ails = ail_obj.search([('product_margin', '=', 0),
                               ('invoice_id.type', 'in', ['out_invoice','out_refund'])])
        for ail in ails:
            ail._compute_product_margin()
            _logger.info('Fixing %s on %s' % (ail.product_id.default_code, ail.date_invoice))



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
