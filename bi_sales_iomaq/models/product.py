# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        'bi_sales_iomaq.brand',
        string='Brand',
        help='Brand of the product',
        store=True,
    )

    cost_fixed = fields.Boolean(
        default=False
    )

    @staticmethod
    def check_a_bit_plus(a, b):
        # Chequea que a sea 20% mayor que b
        return a > b * 1.2

    @api.model
    def fix_historic_cost(self):
        """ Corrige los precios de costo porque a veces estan 100 veces arriba
            de lo que debe ser, cosa de mandinga.

            recorre todos los productos y verifica en tres lugares:

            product.template.bulonfer_cost
            product.seller_ids.supplierinfo.price
            stock.quant.price

            si el precio es mayor que el costo obtenido de la factura o del
            sistema lo cambia teniendo en cuenta que el costo no sea cero.
        """
        _logger.info('START FIXING COSTS')
        # borrar los que estan cerrados
        supp_obj = self.env['product.supplierinfo']
        supp = supp_obj.search([('date_end', '!=', False)])
        print 'borrando >>>>>', len(supp)
        supp.unlink()

        prods = self.search([('cost_fixed', '=', False)], limit=500)
        for prod in prods:
            prod.cost_fixed = True
            # si tengo el costo de la factura lo tomo
            cost = 0
            if prod.system_cost:
                cost = prod.system_cost
            else:
                if prod.bulonfer_cost:
                    # si nunca lo compre tomo el costo de hoy
                    cost = prod.bulonfer_cost
            # arreglo las cosas solo si tengo costo
            if cost:
                # si mi costo historico es mayor que el mejor costo, lo corrijo
                if self.check_a_bit_plus(prod.standard_price, cost):
                    _logger.info('FIXING PRODUCT %s' % prod.default_code)
#                    print 'PRODUCT >>>>>>>', prod.default_code, \
#                        'hist=', prod.standard_price, \
#                        'hoy=', prod.bulonfer_cost, \
#                        'cost=', cost
                    prod.standard_price = cost

                for supplierinfo in prod.seller_ids:
                    if self.check_a_bit_plus(supplierinfo.price, cost):
                        _logger.info('FIXING SUPPINFO %s' % prod.default_code)
#                        print 'SUPPINFO >>>>>>', prod.default_code, \
#                            'hist=', supplierinfo.price, \
#                            'date=', supplierinfo.date_start, \
#                            'cost=', cost
                        supplierinfo.price = cost

                for quant in self.env['stock.quant'].search(
                    [('product_id', '=', prod.id)]):
                    if self.check_a_bit_plus(quant.cost, cost):
                        _logger.info('FIXING QUANT %s' % prod.default_code)
#                        print 'QUANT >>>>>>>>>', prod.default_code, \
#                            'hist=', quant.cost, \
#                            'date=', quant.in_date, \
#                            'cost=', cost
                        quant.cost = cost
