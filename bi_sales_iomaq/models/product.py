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

    @api.model
    def fix_historic_cost(self):
        """ Corrige los precios de costo lo mejor que puede.
            recorre todos los productos y verifica en tres lugares:

            product.template.bulonfer_cost
            product.seller_ids.supplierinfo.price
            stock.quant.price

            Plancha los costos con los de la factura
        """
        _logger.info('START FIXING COSTS')
        # borrar los que estan cerrados
        #supp_obj = self.env['product.supplierinfo']
        #supp = supp_obj.search([('date_end', '!=', False)])
        #supp.unlink()

        prods = self.search([('cost_fixed', '=', False)], limit=450)
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

            # corrijo mi costo historico
            _logger.info('FIXING PRODUCT %s' % prod.default_code)
            prod.standard_price = cost

            for supplierinfo in prod.seller_ids:
                supplierinfo.price = cost

            for quant in self.env['stock.quant'].search([
                    ('product_tmpl_id', '=', prod.id)]):
                quant.cost = cost

        _logger.info('STOP FIXING COSTS')
