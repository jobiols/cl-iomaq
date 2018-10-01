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
#   oe -Q product_currency_fix -c iomaq -d iomaq_test
#

import os


class TestBusiness(TransactionCase):
    """ Cada metodo de test corre en su propia transacción y se hace rollback
        despues de cada uno.
    """

    def setUp(self):
        """ Este setup corre antes de cada método ---------------------------00
        """
        super(TestBusiness, self).setUp()
        self.prod_obj = self.env['product.template']

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

        # configurar valuacion de inventario perpetuo
        self.env['ir.config_parameter'].set_param(
            'group_stock_inventory_valuation', 1)

    def test_01_perpetual_inventory(self):
        """ Testear que el costo del producto vaya al quant al ingresar la
             mercaderia, en las dos monedas, company y product.
        """
        cost = 5000.0

        vendor = self.env['res.partner'].search([('name', '=', 'Agrolait')])
        vendor.ref = 'AGROLAIT'

        # obtener el producto para comprar
        prod = self.env['product.product'].search(
            [('default_code', '=', 'A1090')])

        # definir el precio en dolares.
        prod.product_tmpl_id.force_currency_id = 3
        prod.product_tmpl_id.set_prices(cost, 'AGROLAIT')

        # crear una orden de compra
        po = self.env['purchase.order'].create({
            'partner_id': vendor.id,
        })

        pol = {
            'name': '/',
            'product_id': prod.id,
            'product_uom': prod.uom_id.id,
            'price_unit': prod.standard_price,
            'product_qty': 1,
            'date_planned': '2018-01-01'
        }
        po.order_line = [(0, 0, pol)]
        po.button_confirm()
        picking_in = po.picking_ids

        # Confirm and do incoming shipment.
        picking_in.action_confirm()
        picking_in.do_transfer()

        # obtener el quant
        tmpl = prod.product_tmpl_id
        q = self.prod_obj.oldest_quant(tmpl)

        # company currency ARS
        cc = vendor.company_id.currency_id
        # product currency USD
        pc = prod.currency_id

        self.assertEqual(q.cost, pc.compute(cost, cc))
        self.assertAlmostEqual(q.cost_product, cost, places=3)
