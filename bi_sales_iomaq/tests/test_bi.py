# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

from openerp.tests.common import TransactionCase


#    Forma de correr el test
#    -----------------------
#
#   Definir un subpackage tests que será inspeccionado automáticamente por
#   modulos de test los modulos de test deben empezar con test_ y estar
#   declarados en el __init__.py, como en cualquier package.
#
#   Hay que crear una base de datos no importa el nombre (por ejemplo
#   bulonfer_test) vacia y con el modulo que se va a testear instalado
#   (por ejemplo product_autoload).
#
#   El usuario admin tiene que tener password admin, Language English, Country
#   United States.
#
#   Correr el test con:
#
#   oe -Q bi_sales_iomaq -c iomaq -d iomaq_test
#


class TestBusiness(TransactionCase):
    """ Cada metodo de test corre en su propia transacción y se hace rollback
        despues de cada uno.
    """

    def setUp(self):
        """ Este setup corre antes de cada método ---------------------------00
        """
        super(TestBusiness, self).setUp()
        self.prod_obj = self.env['product.template']

        # configurar valuacion de inventario perpetuo
        self.env['ir.config_parameter'].set_param(
            'group_stock_inventory_valuation', 1)

        account_journal_obj = self.env['account.journal']
        journal = account_journal_obj.create({
            'name': 'inventario',
            'type': 'general',
            'code': 'INV'
        })

        # categoria para probar inventario permanente producto A1090
        categ_obj = self.env['product.category']
        account_obj = self.env['account.account']
        stock = account_obj.search([('code', '=', '1.1.05.01.010')])
        input = account_obj.search([('code', '=', '1.1.05.01.020')])
        output = account_obj.search([('code', '=', '1.1.05.01.030')])
        categ_data = {
            'property_stock_account_input_categ_id': input,
            'property_stock_account_output_categ_id': output,
            'property_stock_valuation_account_id': stock,
            'property_cost_method': 'real',
            'removal_strategy_id': 1,
            'property_valuation': 'real_time',
            'property_stock_journal': journal.id
        }
        categ = categ_obj.search([('id', '=', 6)])
        categ.write(categ_data)

        # agregar un journal
        account_journal_obj = self.env['account.journal']
        account_journal_obj.create({
            'name': 'ventas',
            'type': 'sale',
            'point_of_sale_type': 'manual',
            'point_of_sale_number': 1,
            'code': 'VEN01'
        })

        # agregar cuentas contables
        account_account_obj = self.env['account.account']
        receivable = account_account_obj.create({
            'internal_type': 'receivable',
            'name': 'cuenta',
            'code': '6464.1',
            'user_type_id': 2,
            'reconcile': True
        })
        payable = account_account_obj.create({
            'internal_type': 'payable',
            'name': 'cuenta',
            'code': '6464.2',
            'user_type_id': 2,
            'reconcile': True
        })
        # agregar cuentas a pagar/cobrar en cliente
        partner_obj = self.env['res.partner']
        self.vendor = partner_obj.search([('name', '=', 'Agrolait')])
        self.vendor.property_account_receivable_id = receivable
        self.vendor.property_account_payable_id = payable
        self.vendor.ref = 'AGROLAIT'

        self.client = partner_obj.search([('name', '=', 'ADHOC SA')])
        self.client.property_account_receivable_id = receivable
        self.client.property_account_payable_id = payable

        # configurar valuacion de inventario perpetuo
        self.env['ir.config_parameter'].set_param(
            'group_stock_inventory_valuation', 1)

    def get_quants(self, prod):
        return self.env['stock.quant'].search(
            [('product_id', '=', prod.id),
             ('location_id.usage', '=', 'internal')])

    def ingresar_producto_a_stock(self, prod, qty):
        # comprar el producto -------------------------------------------------
        # crear una orden de compra
        po = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
        })
        cc = prod.company_id.currency_id
        pc = prod.currency_id
        pol = {
            'name': '/',
            'product_id': prod.id,
            'product_uom': prod.uom_id.id,
            'price_unit': pc.compute(prod.bulonfer_cost, cc, round=False),
            'product_qty': qty,
            'date_planned': '2018-01-01'
        }
        po.order_line = [(0, 0, pol)]

        # Confirm and do incoming shipment.
        po.button_confirm()
        picking_in = po.picking_ids
        picking_in.action_confirm()
        picking_in.do_transfer()

    def create_so(self, prod, qty):
        # crear una orden de venta
        sol = {
            'name': '/',
            'product_id': prod.id,
            'product_uom': prod.uom_id.id,
            'product_uom_qty': qty,
        }
        return self.env['sale.order'].create({
            'partner_id': self.client.id,
            'order_line': [(0, 0, sol)]
        })

    def validate_so(self, so):
        # validar la orden de venta
        so.action_confirm()
        picking_out = so.picking_ids
        picking_out.action_confirm()
        picking_out.do_transfer()

    def test_01_ingreso_de_producto_normal(self):
        """ Testear que el costo del producto vaya al quant al ingresar la
             mercaderia, en las dos monedas, company y product.
        """
        cost1 = 5000.0
        price1 = 7000.0
        cost2 = 6000.0
        price2 = 8400.0

        # obtener el producto para comprar y vender
        prod = self.env['product.product'].search(
            [('default_code', '=', 'A1090')])
        tmpl = prod.product_tmpl_id
        # forzar al producto en dolares
        tmpl.force_currency_id = 3

        tmpl.property_account_income_id = 1
        tmpl.property_account_expense_id = 2

        # company currency ARS
        cc = prod.company_id.currency_id
        # product currency USD
        pc = prod.currency_id

        # ingresar producto a precio 1
        prod.product_tmpl_id.set_prices(cost1, 'AGROLAIT', price=price1)
        self.ingresar_producto_a_stock(prod, 1)

        # verificar el precio del quant
        q = self.get_quants(prod)
        self.assertEqual(q.cost, pc.compute(cost1, cc))
        self.assertAlmostEqual(q.cost_product, cost1, places=3)

        # ingresar producto a precio 2
        prod.product_tmpl_id.set_prices(cost2, 'AGROLAIT', price=price2)
        self.ingresar_producto_a_stock(prod, 2)

        # verificar el precio del quant
        q = self.get_quants(prod)
        self.assertEqual(q[1].cost, pc.compute(cost2, cc))
        self.assertAlmostEqual(q[1].cost_product, cost2, places=3)

        # obtener el quant mas antiguo (es el primero que puse)
        q = self.prod_obj.oldest_quant(tmpl)
        self.assertEqual(q.cost, pc.compute(cost1, cc))
        self.assertAlmostEqual(q.cost_product, cost1, places=3)

        # vender el producto y verificar que se muevan los costos--------------

        so1 = self.create_so(prod, 1)
        self.validate_so(so1)
        # El standard price sigue en 5000
        self.assertEqual(prod.standard_price, pc.compute(cost1, cc))
        self.assertEqual(prod.standard_product_price, cost1)

        # Crear las facturas y verificar BI

        id = so1.action_invoice_create()
        inv = self.env['account.invoice'].browse(id[0])
        inv.signal_workflow('invoice_open')

        ail_obj = self.env['account.invoice.line']
        ail = ail_obj.search([('product_id', '=', prod.id)])

        # en la linea de factura precio es el ultimo
        self.assertEqual(ail.price_subtotal_signed, pc.compute(price2, cc))
        # costo es el mas antiguo
        self.assertEqual(ail.product_id.standard_price, pc.compute(cost1, cc))
        # el margen es mayor que el oficial
        self.assertAlmostEqual(ail.product_margin, price2 / cost1 - 1,
                               places=4)

        bi_obj = self.env['account.invoice.line.report.iomaq']
        bi = bi_obj.search([('product_id', '=', prod.id)])

        # precio
        self.assertEqual(bi.price_total, pc.compute(price2, cc))
        # costo
        self.assertEqual(bi.cost_total, pc.compute(cost1, cc))
        # margen
        self.assertEqual(bi.margin_total, pc.compute(price2 - cost1, cc))

    def test_02_ingreso_de_producto_consignacion(self):
        """ Testear que el costo del producto vaya al quant al ingresar la
             mercaderia, en las dos monedas, company y product.
             costo del producto en pesos.
             Mercaderia en consignacion.
        """
        vendor = self.env['res.partner'].search([('ref', '=', 'AGROLAIT')])
        vendor.business_mode = 'consignment'

        cost1 = 5000.0
        price1 = 7000.0
        cost2 = 6000.0
        price2 = 8400.0

        # obtener el producto para comprar y vender
        prod = self.env['product.product'].search(
            [('default_code', '=', 'A1090')])
        tmpl = prod.product_tmpl_id

        # forzar al producto en pesos
        tmpl.force_currency_id = 20

        # agregarle las cuentas contables solo para que genere la factura
        tmpl.property_account_income_id = 1
        tmpl.property_account_expense_id = 2

        # company currency ARS
        cc = prod.company_id.currency_id
        # product currency USD
        pc = prod.currency_id

        # ingresar producto a precio 1
        prod.product_tmpl_id.set_prices(cost1, 'AGROLAIT', price=price1)
        self.ingresar_producto_a_stock(prod, 1)

        # verificar el precio del quant
        q = self.get_quants(prod)
        self.assertEqual(q.cost, pc.compute(cost1, cc))
        self.assertAlmostEqual(q.cost_product, cost1, places=3)

        # ingresar producto a precio 2
        prod.product_tmpl_id.set_prices(cost2, 'AGROLAIT', price=price2)
        self.ingresar_producto_a_stock(prod, 2)

        # verificar el precio del quant
        q = self.get_quants(prod)
        self.assertEqual(q[1].cost, pc.compute(cost2, cc))
        self.assertAlmostEqual(q[1].cost_product, cost2, places=3)

        # obtener el quant mas antiguo (es el primero que puse)
        q = self.prod_obj.oldest_quant(tmpl)
        self.assertEqual(q.cost, pc.compute(cost1, cc))
        self.assertAlmostEqual(q.cost_product, cost1, places=3)

        # vender el producto y verificar que se muevan los costos--------------

        so1 = self.create_so(prod, 1)
        self.validate_so(so1)
        # El standard price sigue en 5000
        self.assertEqual(prod.standard_price, pc.compute(cost1, cc))
        self.assertEqual(prod.standard_product_price, cost1)

        # Crear las facturas y verificar BI

        id = so1.action_invoice_create()
        inv = self.env['account.invoice'].browse(id[0])
        inv.signal_workflow('invoice_open')

        ail_obj = self.env['account.invoice.line']
        ail = ail_obj.search([('product_id', '=', prod.id)])

        # en la linea de factura precio es el ultimo
        self.assertEqual(ail.price_subtotal_signed, pc.compute(price2, cc))
        # costo es el mas antiguo ???? esta mal esto ???? seria el mas nuevo.
        self.assertEqual(ail.product_id.standard_price, pc.compute(cost1, cc))
        # el margen se calcula con el ultimo precio porque es consignacion
        self.assertAlmostEqual(ail.product_margin, price2 / cost2 - 1,
                               places=4)

        bi_obj = self.env['account.invoice.line.report.iomaq']
        bi = bi_obj.search([('product_id', '=', prod.id)])

        # precio
        self.assertEqual(bi.price_total, pc.compute(price2, cc))
        # costo
        self.assertEqual(bi.cost_total, pc.compute(cost2, cc))
        # margen
        self.assertEqual(bi.margin_total, pc.compute(price2 - cost2, cc))

    def test_03_ingreso_de_producto_consignacion(self):
        """ Testear que el costo del producto vaya al quant al ingresar la
             mercaderia, en las dos monedas, company y product.
             costo del producto en dolares.
             Mercaderia en consignacion.
        """
        vendor = self.env['res.partner'].search([('ref', '=', 'AGROLAIT')])
        vendor.business_mode = 'consignment'

        cost1 = 5000.0
        price1 = 7000.0
        cost2 = 6000.0
        price2 = 8400.0

        # obtener el producto para comprar y vender
        prod = self.env['product.product'].search(
            [('default_code', '=', 'A1090')])
        tmpl = prod.product_tmpl_id

        # forzar al producto en dolares
        tmpl.force_currency_id = 3

        # agregarle las cuentas contables solo para que genere la factura
        tmpl.property_account_income_id = 1
        tmpl.property_account_expense_id = 2

        # company currency ARS
        cc = prod.company_id.currency_id
        # product currency USD
        pc = prod.currency_id

        # ingresar producto a precio 1
        prod.product_tmpl_id.set_prices(cost1, 'AGROLAIT', price=price1)
        self.ingresar_producto_a_stock(prod, 1)

        # verificar el precio del quant
        q = self.get_quants(prod)
        self.assertEqual(q.cost, pc.compute(cost1, cc))
        self.assertAlmostEqual(q.cost_product, cost1, places=3)

        # ingresar producto a precio 2
        prod.product_tmpl_id.set_prices(cost2, 'AGROLAIT', price=price2)
        self.ingresar_producto_a_stock(prod, 2)

        # verificar el precio del quant
        q = self.get_quants(prod)
        self.assertEqual(q[1].cost, pc.compute(cost2, cc))
        self.assertAlmostEqual(q[1].cost_product, cost2, places=3)

        # obtener el quant mas antiguo (es el primero que puse)
        q = self.prod_obj.oldest_quant(tmpl)
        self.assertEqual(q.cost, pc.compute(cost1, cc))
        self.assertAlmostEqual(q.cost_product, cost1, places=3)

        # vender el producto y verificar que se muevan los costos--------------

        so1 = self.create_so(prod, 1)
        self.validate_so(so1)
        # El standard price sigue en 5000
        self.assertEqual(prod.standard_price, pc.compute(cost1, cc))
        self.assertEqual(prod.standard_product_price, cost1)

        # Crear las facturas y verificar BI

        id = so1.action_invoice_create()
        inv = self.env['account.invoice'].browse(id[0])
        inv.signal_workflow('invoice_open')

        ail_obj = self.env['account.invoice.line']
        ail = ail_obj.search([('product_id', '=', prod.id)])

        # en la linea de factura precio es el ultimo
        self.assertEqual(ail.price_subtotal_signed, pc.compute(price2, cc))
        # costo es el mas antiguo ???? esta mal esto ???? seria el mas nuevo.
        self.assertEqual(ail.product_id.standard_price, pc.compute(cost1, cc))
        # el margen se calcula con el ultimo precio porque es consignacion
        self.assertAlmostEqual(ail.product_margin, price2 / cost2 - 1,
                               places=4)

        bi_obj = self.env['account.invoice.line.report.iomaq']
        bi = bi_obj.search([('product_id', '=', prod.id)])

        # precio
        self.assertEqual(bi.price_total, pc.compute(price2, cc))
        # costo
        self.assertAlmostEqual(bi.cost_total, pc.compute(cost2, cc), places=2)
        # margen
        self.assertAlmostEqual(bi.margin_total, pc.compute(price2 - cost2, cc),
                               places=1)

    def test_04_get_fix_historic_price(self):
        """ Testear fix get_fix_historic_price
        """

        # buscar un producto cualquiera
        pid = self.env['product_product'].search([], limit=1)

        # cargarle datos historicos
        cost = 1000
        price = 1500

        pid.product_tmpl_id.set_prices(cost, 'AGROLAIT', price=price)
