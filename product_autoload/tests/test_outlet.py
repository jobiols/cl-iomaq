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


class TestOutlet(TransactionCase):
    """ Cada metodo de test corre en su propia transacción y se hace rollback
        despues de cada uno.
    """

    def setUp(self):
        """ Este setup corre antes de cada método ---------------------------00
        """
        super(TestOutlet, self).setUp()

