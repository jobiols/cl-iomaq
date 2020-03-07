# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    business_mode = fields.Selection([
        ('standard', 'Normal'),
        ('consignment', 'Consignación')],
        help="Modo de venta\n-Normal\n-Consignación",
        string='Modo de Venta',
        default='standard'
    )
