# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

#    Forma de correr el test
#    -----------------------
#
#   Definir un subpackage tests que será inspeccionado automáticamente por
#   modulos de test los modulos de test deben enpezar con test_ y estar
#   declarados en el __init__.py, como en cualquier package.
#
#   Hay que crear una base de datos no importa el nombre pero se sugiere
#   [nombre cliente]_test_[nombre modulo] que debe estar vacia pero con el
#   modulo que se quiere testear instalado.
#
#   Debe tener usuario admin y password admin
#
#   Arrancar el test con:
#
#   oe -Q kpis_panel -c iomaq -d iomaq_test
#
from openerp.tests import common


class Test_kpis(common.TransactionCase):
    """ Cada metodo de test corre en su propia transacción y se hace rollback
        despues de cada uno.
    """

    def setUp(self):
        super(Test_kpis, self).setUp()

        self.category = self.env['res.partner.category'].create(
            {'name': 'MERCADERIA'})

        self.vendor1 = self.env['res.partner'].create(
            {'name': 'proveedor1',
             'category_id': [(6, 0, [self.category.id])]}
        )
        self.vendor2 = self.env['res.partner'].create(
            {'name': 'proveedor2',
             'category_id': [(6, 0, [self.category.id])]}
        )
        self.vendor3 = self.env['res.partner'].create(
            {'name': 'proveedor3'}
        )

        self.kpi1 = self.env['kpis_panel.kpis'].create({
            'vendor_id': self.vendor1.id}
        )
        self.kpi3 = self.env['kpis_panel.kpis'].create({
            'vendor_id': self.vendor3.id}
        )

    def test_01_update(self):
        kpis = self.env['kpis_panel.kpis']
        kpis.update_reported_vendors()
