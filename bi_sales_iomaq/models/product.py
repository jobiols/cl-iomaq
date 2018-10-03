# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api
import logging
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        'bi_sales_iomaq.brand',
        string='Brand',
        help='Brand of the product',
        store=True,
    )

    final_price = fields.Float(
        string='Price tax included',
        compute='_compute_final_price',
        digits=dp.get_precision('Product Price'),
        help='Final Price. This is the public price with tax',
    )

    @api.multi
    def _compute_final_price(self):
        for prod in self:
            cc = prod.company_id.currency_id
            pc = prod.currency_id

            # obtener el precio de lista en moneda de la compa~nia
            lp = pc.compute(prod.list_price, cc, round=False)

            # poner el precio iva incluido
            tax = prod.taxes_id[0].amount if prod.taxes_id else 0
            prod.final_price = lp * (1 + tax / 100)

    @api.model
    def fix_historic_cost(self):
        """ Corrige costos de los quants en STIHL
            recorre todos los productos con currency USD

            pone standard price y los quants
            Para correr a mano
        """
        prods_obj = self.env['product.template']
        prods = prods_obj.search([('default_code', 'like', '-STIHL')])
        for prod in prods:
            cost = prod.bulonfer_cost
            prod.standard_product_price = cost

            cc = prod.company_id.currency_id

            for supplierinfo in prod.seller_ids:
                supplierinfo.price = cost

            for quant in self.env['stock.quant'].search([
                ('product_tmpl_id', '=', prod.id)]):
                pc = prod.currency_id.with_context(date=quant.in_date)

                quant.cost = pc.compute(cost, cc, round=False)
                prod.standard_price = pc.compute(cost, cc, round=False)
                quant.cost_product = cost

            _logger.info('product like %s' % prod.default_code)

        prods_obj = self.env['product.template']
        prods = prods_obj.search([('default_code', 'not like', '-STIHL')])

        # TODO Esto tarda a~nos !!!!!!!!!!!!
        for prod in prods:
            prod.standard_product_price = prod.standard_price
            _logger.info('product not like %s' % prod.default_code)
