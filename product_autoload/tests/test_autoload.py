# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

from openerp.tests.common import TransactionCase
from ..models.mappers import ProductMapper, MAP_NAME, MAP_UPV, \
    MAP_STANDARD_PRICE, MAP_WEIGHT
import csv
import os


#   Forma de correr el test
#   -----------------------
#
#   Definir un subpackage tests que será inspeccionado automáticamente por
#   modulos de test los modulos de test deben empezar con test_ y estar
#   declarados en el __init__.py, como en cualquier package.
#
#   Hay que crear una base de datos no importa el nombre (usualmente el nombre
#   es [cliente]_test_[modulo a testear]
#
#   El usuario admin tiene que tener password admin, Language Spanish, Country
#   Argentina y Load demostration data.
#
#   Correr el test con:
#
#   oe -Q product_autoload -c iomaq -d iomaq_test
#


class TestBusiness(TransactionCase):
    """ Cada metodo de test corre en su propia transacción y se hace rollback
        despues de cada uno.
    """

    def setUp(self):
        """ Este setup corre antes de cada método ---------------------------00
        """
        super(TestBusiness, self).setUp()

        # Agregar al admin al grupo de crear productos para que funcione
        # el test.
        create_prod_group = self.env['res.groups'].search(
            [('name', '=', 'Crear productos manualmente')])
        admin = self.env['res.users'].search([('id', '=', 1)])
        create_prod_group.users += admin

        # obtener el path al archivo de datos
        self._data_path = os.path.abspath(__file__)
        self._data_path = os.path.dirname(self._data_path)
        self._data_path = self._data_path.replace('tests', 'data/')

        self.env['ir.config_parameter'].set_param('data_path', self._data_path)
        self.env['ir.config_parameter'].set_param('email_notification',
                                                  'zz@pp.com')
        self.env['ir.config_parameter'].set_param('email_from', 'zz@pp.com')

        self._vendor = self.env['res.partner'].search(
            [('ref', '=', 'BULONFER')])

        self._supinfo = self.env['product.supplierinfo']

        # definimos una linea del archivo para probar
        self.line = [
            '123456',  # Código del producto
            'nombre-producto',  # Nombre del producto
            'Descripción del producto',  # Descripción del producto
            '500.22',  # Precio de costo
            '100',  # UPV Agrupacion mayorista
            '200.50',  # Peso bruto en kg
            '125.85',  # Volumen m3
            '100',  # Bulto Mayorista
            '5',  # Bulto Minorista
            '102.7811.jpg',  # Nombre de la imagen
            '60',  # Garantia (meses)
            '15.5',  # IVA %
            '133',  # idRubro
            '2018-25-01 13:10:55']  # Timestamp actualización

        self.manager_obj = self.env['product_autoload.manager']
        self.prod_obj = self.env['product.template']

        account_journal_obj = self.env['account.journal']
        account_journal_obj.create({
            'name': 'inventario',
            'type': 'general',
            'code': 'INV'
        })

    def add_quant(self, prod):
        quant_obj = self.env['stock.quant']
        quant_obj.create({'product_tmpl_id': prod.id,
                          'location_id.usage': 'internal',
                          'location_id': 12,
                          'qty': 1,
                          'product_id': prod.product_variant_ids.id})

    def test_01_product_mapper(self):
        """ Chequear creacion de ProductMapper ------------------------------01
        """

        # creamos un dict con los valores pasados por el prod
        val = {
            'default_code': self.line[0],
            'name': self.line[1],
            'description_sale': self.line[2],
            'bulonfer_cost': float(self.line[3]) / float(self.line[4]),
            'upv': float(self.line[4]),
            'weight': float(self.line[5]),
            'volume': float(self.line[6]),
            'wholesaler_bulk': float(self.line[7]),
            'retail_bulk': float(self.line[8]),
            '_image_name': self.line[9],
            'warranty': float(self.line[10]),
            'iva': float(self.line[11]),
            'item_code': self.line[12],
            'write_date': self.line[13]
        }

        # cargamos la linea en el mapper
        prod = ProductMapper(self.line, self._data_path, self._vendor)

        # chequeamos que cada propiedad este correcta
        self.assertEqual(prod.default_code, val['default_code'])
        self.assertEqual(prod.name, val['name'])
        self.assertEqual(prod.description_sale, val['description_sale'])
        self.assertEqual(prod.bulonfer_cost, val['bulonfer_cost'])
        self.assertEqual(prod.upv, val['upv'])
        self.assertEqual(prod.weight, val['weight'])
        self.assertEqual(prod.volume, val['volume'])
        self.assertEqual(prod.wholesaler_bulk, val['wholesaler_bulk'])
        self.assertEqual(prod.retail_bulk, val['retail_bulk'])
        self.assertEqual(prod.warranty, val['warranty'])
        self.assertEqual(prod.iva, val['iva'])
        self.assertEqual(prod.item_code, val['item_code'])
        self.assertEqual(prod.write_date, val['write_date'])

        # verificamos que los datos sean correctos
        val = prod.values()
        for item in val:
            self.assertEqual(prod.values()[item], val[item])

        # verificar ademas los default values
        self.assertEqual(val['type'], 'product')
        self.assertEqual(val['invoice_policy'], 'order')
        self.assertEqual(val['purchase_method'], 'purchase')

    def test_02_(self):
        """ string no unicode -----------------------------------------------02
        """
        line = self.line
        line[MAP_NAME] = b'\x00\xFF\x00\xFF'  # string no utf-8
        with self.assertRaises(Exception):
            ProductMapper(line, self._data_path, self._vendor,
                          self._supinfo)

    def test_03_(self):
        """ numero es un string ---------------------------------------------03
        """
        line = self.line
        line[MAP_UPV] = 'HHH'  # debe ser numero y es string
        with self.assertRaises(Exception):
            ProductMapper(line, self._data_path, self._vendor,
                          self._supinfo)

    def test_04_(self):
        """ currency es un string -------------------------------------------04
        """
        line = self.line
        line[MAP_STANDARD_PRICE] = 'HHH'  # debe ser currency y es string
        with self.assertRaises(Exception):
            ProductMapper(line, self._data_path, self._vendor,
                          self._supinfo)

    def test_05_(self):
        """ float es un string ----------------------------------------------05
        """
        line = self.line
        line[MAP_WEIGHT] = 'HHH'  # debe ser numero y es string
        with self.assertRaises(Exception):
            ProductMapper(line, self._data_path, self._vendor,
                          self._supinfo)

    def test_06_update(self):
        """ Chequear que NO replique registros viejos------------------------06
        """
        self.env['ir.config_parameter'].set_param('last_replication',
                                                  '2018-02-26 16:13:21')
        self.env['ir.config_parameter'].set_param('import_only_new', True)
        self.manager_obj.run_files()

        # verificar que se creo el archivo
        file = '2018-08-30-data.csv'
        created = os.path.isfile(self._data_path + file)
        self.assertTrue(created)

        # borrarlo
        os.remove(self._data_path + file)

    def test_08_update_product(self):
        """ Chequear que SI replique si fuerzo la replicacion----------------08
        """
        self.env['ir.config_parameter'].set_param('last_replication',
                                                  '2018-09-26 16:13:21')
        # pero aca lo estoy forzando a que replique
        self.env['ir.config_parameter'].set_param('import_only_new', False)

        self.manager_obj.run_files()
        # verificar que se creo el archivo
        files = ['2018-01-26-data.csv', '2018-08-30-data.csv']

        for file in files:
            created = os.path.isfile(self._data_path + file)
            self.assertTrue(created)
            # borrarlo
            os.remove(self._data_path + file)

    def test_085_verificar_borrado(self):
        """ Borrado del archivo diario al procesarlo completamente
        """
        self.env['ir.config_parameter'].set_param('last_replication',
                                                  '2018-01-25 16:13:21')
        # debe generar los dos archivos
        self.manager_obj.run_files()

        # proceso el mas antiguo
        self.manager_obj.run(process_qty=8)
        # una vez mas para que se salte una linea y lo borre
        self.manager_obj.run(process_qty=8)
        # proceso el otro y se borra solo
        self.manager_obj.run(process_qty=8)
        # este no deberia hacer nada
        self.manager_obj.run()

        # verificar que no quedo ningun archivo
        files = ['2018-01-26-data.csv', '2018-08-30-data.csv']
        for file in files:
            created = os.path.isfile(self._data_path + file)
            self.assertFalse(created)

        prod_obj = self.env['product.template']

        # verificar que se cargaron los productos
        prod = prod_obj.search([('default_code', '=', '102.B.12')])
        self.assertTrue(prod)
        prod = prod_obj.search([('default_code', '=', '102.7811')])
        self.assertTrue(prod)

    def test_09_categories(self):
        """ Actualizacion de categorias y precios de lista ------------------09
        """
        prod_obj = self.env['product.template']

        self.manager_obj.run_files()
        self.manager_obj.run(process_qty=8)
        self.manager_obj.run(process_qty=8)
        self.manager_obj.run(process_qty=8)

        # verificar precios
        prod = prod_obj.search([('default_code', '=', '102.B.12')])
        self.assertEqual(prod.bulonfer_cost, 2.2372)
        self.assertAlmostEqual(prod.list_price, 2.2372 * 1.5, places=2)

        prod = prod_obj.search([('default_code', '=', '106.32')])
        self.assertAlmostEqual(prod.bulonfer_cost, 15.0620, places=12)
        self.assertAlmostEqual(prod.list_price, 15.0620 * 1.5, places=2)

        self.manager_obj.update_categories()

        # verificar creacion de categorias
        categ_obj = self.env['product.category']
        categ = categ_obj.search([('name', '=', u'Bulonería'),
                                  ('parent_id', '=', False)])
        self.assertEqual(categ.property_cost_method, 'real')
        self.assertEqual(categ.removal_strategy_id.method, 'fifo')
        self.assertEqual(categ.property_valuation, 'real_time')
        self.assertEqual(categ.property_stock_account_input_categ_id.code,
                         u'1.1.05.01.020')
        self.assertEqual(categ.property_stock_account_output_categ_id.code,
                         u'1.1.05.01.030')
        self.assertEqual(categ.property_stock_valuation_account_id.code,
                         u'1.1.05.01.010')

        categ = categ_obj.search([('name', '=', u'ARANDELAS'),
                                  ('parent_id.name', '=', u'Bulonería')])
        self.assertEqual(categ.property_cost_method, 'real')
        self.assertEqual(categ.removal_strategy_id.method, 'fifo')
        self.assertEqual(categ.property_valuation, 'real_time')
        self.assertEqual(categ.property_stock_account_input_categ_id.code,
                         u'1.1.05.01.020')
        self.assertEqual(categ.property_stock_account_output_categ_id.code,
                         u'1.1.05.01.030')
        self.assertEqual(categ.property_stock_valuation_account_id.code,
                         u'1.1.05.01.010')

        categ = categ_obj.search([('name', '=', u'ARANDELA AUTOMOTOR FIXO'),
                                  ('parent_id.name', '=', u'ARANDELAS')])
        self.assertEqual(categ.property_cost_method, 'real')
        self.assertEqual(categ.removal_strategy_id.method, 'fifo')
        self.assertEqual(categ.property_valuation, 'real_time')
        self.assertEqual(categ.property_stock_account_input_categ_id.code,
                         u'1.1.05.01.020')
        self.assertEqual(categ.property_stock_account_output_categ_id.code,
                         u'1.1.05.01.030')
        self.assertEqual(categ.property_stock_valuation_account_id.code,
                         u'1.1.05.01.010')

    def test_10_cambia_margen(self):
        """ Testear cambio de margen de ganancia-----------------------------10
        """
        self.manager_obj.run_files()
        self.manager_obj.run()
        self.manager_obj.run()
        self.manager_obj.update_categories()

        prod = self.prod_obj.search([('default_code', '=', '106.24')])
        self.assertAlmostEqual(prod.bulonfer_cost, 150.62)
        self.assertAlmostEqual(prod.bulonfer_cost * 1.5, prod.list_price,
                               places=2)

        self.manager_obj.run_files()
        self.manager_obj.run(item='item_changed.csv')
        self.manager_obj.run(item='item_changed.csv')
        self.manager_obj.update_categories()

        prod = self.prod_obj.search([('default_code', '=', '106.24')])
        self.assertAlmostEqual(prod.bulonfer_cost * 1.6, prod.list_price,
                               places=2)

    def test_11_barcodes(self):
        """ Testear barcode duplicado ---------------------------------------11
        """
        self.manager_obj.run_files()
        self.manager_obj.run(productcode='productcode_changed.csv')
        self.manager_obj.run(productcode='productcode_changed.csv')

    def test_13_costos(self):
        """ Testear que cargue bien los costos ------------------------------13
        """
        self.manager_obj.run_files()
        self.manager_obj.run()
        self.manager_obj.run()
        self.manager_obj.update_categories()
        prod = self.prod_obj.search([('default_code', '=', '102.7811')])
        self.assertAlmostEqual(prod.bulonfer_cost, 8.98, places=2)
        self.assertAlmostEqual(prod.standard_price, 8.98, places=2)

    def test_14_closest_invoice_line(self):
        """ Testear la funcion ----------------------------------------------14
            date_in 15/09/2018 13:39:12
        """
        # agregar cuentas contables
        account_account_obj = self.env['account.account']
        account = account_account_obj.create({
            'internal_type': 'payable',
            'name': 'cuenta',
            'code': '6464',
            'user_type_id': 2,
            'reconcile': True
        })

        # agregar un journal
        account_journal_obj = self.env['account.journal']
        journal_id = account_journal_obj.create({
            'name': 'ventas',
            'type': 'sale',
            'point_of_sale_type': 'manual',
            'point_of_sale_number': 1,
            'code': 'VEN01'
        })

        # obtener el producto
        prod_prod = self.env['product.product'].search([('id', '=', 12)])

        # crear la linea de la factura
        invoice_line_ids = {
            'product_id': prod_prod.id,
            'quantity': 1,
            'account_id': account.id,
            'price_unit': 123,
            'name': 'producto vendido'
        }

        # crear tres facturas en tres fechas distintas
        account_invoice_object = self.env['account.invoice']
        ai1 = account_invoice_object.create({
            'partner_id': 6,
            'date_invoice': '2018-09-01',
            'invoice_line_ids': [(0, 0, invoice_line_ids)],
            'journal_id': journal_id.id,
            'account_id': account.id,
        })
        ai2 = account_invoice_object.create({
            'partner_id': 6,
            'date_invoice': '2018-09-10',
            'invoice_line_ids': [(0, 0, invoice_line_ids)],
            'journal_id': journal_id.id,
            'account_id': account.id,
        })
        ai3 = account_invoice_object.create({
            'partner_id': 6,
            'date_invoice': '2018-09-20',
            'invoice_line_ids': [(0, 0, invoice_line_ids)],
            'journal_id': journal_id.id,
            'account_id': account.id,
        })
        ai1.discount_processed = True
        ai2.discount_processed = True
        ai3.discount_processed = True

        # ajustar la fecha del ultimo quant cercana a la fac '2018-09-10'
        tmpl = prod_prod.product_tmpl_id

        q = self.prod_obj.oldest_quant(tmpl)
        q.in_date = '2018-09-12'

        # obtener la linea de la factura con la fecha mas cercana al quant
        # mas viejo.
        invoice_line = self.prod_obj.closest_invoice_line(tmpl, 'not-a-date')
        self.assertEqual(invoice_line.id, ai2.invoice_line_ids.id)

    def test_15_check_996(self):
        """ Los productos 996 deben ser ignorados ---------------------------15
        """
        prod_obj = self.env['product.template']

        # carga los productos donde hay 996
        self.manager_obj.run_files()
        self.manager_obj.run()
        self.manager_obj.run()

        # verificar que NO se carga el 996
        prod = prod_obj.search([('default_code', '=', '996.18.10')])
        self.assertFalse(prod)

    def test_16_(self):
        """ Si baja el precio sin stock hay que actualizar ------------------16
            y poner en oferta
        """

        # replicar todo
        self.env['ir.config_parameter'].set_param(
            'import_only_new', False)

        # chequear el precio original
        self.manager_obj.run_files()
        self.manager_obj.run()
        self.manager_obj.run()
        prod = self.prod_obj.search([('default_code', '=', '102.AF')])
        self.assertAlmostEqual(prod.bulonfer_cost, 7.7832)

        # cargar de nuevo y con precio rebajado
        self.manager_obj.run_files(data='data_baja_precios.csv')
        self.manager_obj.run()
        self.manager_obj.run()

        # como no hay stock se baja el precio y se pone en oferta
        prod = self.prod_obj.search([('default_code', '=', '102.AF')])
        self.assertAlmostEqual(prod.bulonfer_cost, 7.0)
        self.assertEqual(prod.product_variant_ids.state, 'offer')

    def test_17_(self):
        """ Si baja el precio con stock NO hay que actualizar -------------- 17
            y poner en oferta
        """
        # replicar todo
        self.env['ir.config_parameter'].set_param(
            'import_only_new', False)

        # chequear el precio original
        self.manager_obj.run_files()
        self.manager_obj.run()
        self.manager_obj.run()
        prod = self.prod_obj.search([('default_code', '=', '102.AF')])
        self.assertAlmostEqual(prod.bulonfer_cost, 7.7832)

        # hay stock
        self.add_quant(prod)

        # cargar de nuevo y chequear el precio rebajado
        self.manager_obj.run_files(data='data_baja_precios.csv')
        self.manager_obj.run()
        self.manager_obj.run()
        prod = self.prod_obj.search([('default_code', '=', '102.AF')])
        self.assertAlmostEqual(prod.bulonfer_cost, 7.7832)
        self.assertEqual(prod.product_variant_ids.state, 'offer')

    def test_18_(self):
        """ Si el producto esta en oferta y sube el precio ----------------- 18
            sacar de oferta no importa el stock
        """
        # replicar todo
        self.env['ir.config_parameter'].set_param(
            'import_only_new', False)

        # iniciamos con el producto normal
        self.manager_obj.run_files()
        self.manager_obj.run()
        self.manager_obj.run()
        prod = self.prod_obj.search([('default_code', '=', '102.AF')])
        self.assertEqual(prod.product_variant_ids.state, 'sellable')

        # el producto entra en oferta sin stock
        self.manager_obj.run_files(data='data_baja_precios.csv')
        self.manager_obj.run()
        self.manager_obj.run()
        prod = self.prod_obj.search([('default_code', '=', '102.AF')])
        self.assertEqual(prod.product_variant_ids.state, 'offer')
        self.assertAlmostEqual(prod.bulonfer_cost, 7.0)

        # el precio sube, corregir y sacar de oferta
        self.manager_obj.run_files()
        self.manager_obj.run()
        self.manager_obj.run()
        prod = self.prod_obj.search([('default_code', '=', '102.AF')])
        self.assertAlmostEqual(prod.bulonfer_cost, 7.7832)
        self.assertEqual(prod.product_variant_ids.state, 'sellable')

    def test_19_run_files(self):
        """ Testea que se generen los archivos diarios --------------------- 19
        """
        self.manager_obj.run_files()
        with open(self._data_path + '2018-08-30-data.csv', 'r') as file_csv:
            reader = csv.reader(file_csv)
            for line in reader:
                self.assertEqual(line[0], '996.18.10')

        with open(self._data_path + '2018-01-26-data.csv', 'r') as file_csv:
            reader = csv.reader(file_csv)
            for line in reader:
                self.assertEqual(line[0], '102.7811')
                break

    def test_20_get_first_file(self):
        """ Verifica la funcion que encuentra el mas viejo ----------------- 20
        """
        file = self.manager_obj.get_first_file()
        self.assertEqual(file, '2018-01-26-data.csv')
