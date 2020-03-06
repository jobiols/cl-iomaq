# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty = fields.Float(
        string='Fidelizacion %',
        help='Incremento porcentual de precios para este cliente (o '
             'decremento si es negativo)'
    )
