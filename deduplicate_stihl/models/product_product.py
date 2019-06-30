# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

from openerp import api, fields, models, _
from openerp.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    default_code_stihl = fields.Char(
    )

    @api.model
    def write(self, vals):
        """ Evitar la duplicacion de productos stihl
        """
        # obtener el codigo limpio
        if 'default_code' in vals and vals['default_code']:
            code = vals['default_code'].replace('-', '').strip()
            # verificar si existe
            domain = [('default_code_stihl', '=', code)]
            if self.env['product.product'].search(domain):
                raise UserError('El codigo de producto interpretado sin '
                                'los guiones, ya existe')

            # no existe, agregarlo en vals
            vals['default_code_stihl'] = code

        # crear el registro con el super
        return super(ProductProduct, self).write(vals)

    @api.model
    def fix_stihl(self):
        """ Para correr a mano la primera vez
        """
        products = self.env['product.product'].search([])
        for product in products:
            # obtener el codigo limpio
            if product.default_code:
                code = product.default_code.replace('-', '').strip()
                # salvarlo en el producto
                product.default_code_stihl = code
                _logger.info('processing %s' % code)
