# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from openerp import models, fields, api
from datetime import timedelta

_logger = logging.getLogger(__name__)


class Kpis(models.Model):
    _name = 'kpis_panel.kpis'

    vendor_id = fields.Many2one(
        'res.partner',
        domain="[('category_id.name', 'in', ['MERCADERIA'] )]",
        required=True
    )
    total_payable = fields.Float(
        required=True,
        default=0
    )
    stock_valuation = fields.Float(
        required=True,
        string="Stock valuation (sale price w/tax)",
        default=0
    )
    count = fields.Integer(
        required=True,
        default=0
    )
    updated = fields.Datetime(
        default=lambda x: fields.datetime.now(),
        readonly=True,
        required=True
    )

    @property
    def next_kpi_run(self):
        parameter_obj = self.env['ir.config_parameter']
        last = parameter_obj.get_param('last_kpi_run')
        return last if last else '2000-01-01'

    @next_kpi_run.setter
    def next_kpi_run(self, value):
        parameter_obj = self.env['ir.config_parameter']
        parameter_obj.set_param('last_kpi_run', str(value))

    @api.model
    def update_reported_vendors(self):
        """ Actualizar la tabla 'kpis_panel.kpis' con los vendors que tienen
            la etiqueta MERCADERIA
        """
        # agregar los vendors que tienen entiqueta y no estan en kpi
        domain = [('category_id.name', '=', 'MERCADERIA')]
        vendors = self.env['res.partner'].search(domain)
        for vendor in vendors:
            if not self.search([('vendor_id', '=', vendor.id)]):
                self.create({'vendor_id': vendor.id})
                _logger.info('ADDED KPI for %s' % vendor.name)

        # quitar los vendors que estan en kpi y no tienen etiqueta
        for kpi in self.search([]):
            if 'MERCADERIA' not in kpi.vendor_id.category_id.mapped('name'):
                _logger.info('DELETED KPI for %s' % kpi.vendor_id.name)
                kpi.unlink()

    @api.model
    def update(self):
        domain = [('updated', '<=', str(fields.datetime.now()))]
        kpis = self.search(domain, limit=1)

        # procesar uno de los kpis
        for rec in kpis:
            _logger.info('Updating KPIS for %s' % rec.vendor_id.name)

            # obtener todos los productos que se le compran a este vendor y
            # que tienen stock >0
            domain = [('seller_ids.name', '=', rec.vendor_id.id),
                      ('virtual_available', '>', 0)]

            stock_valuation = count = 0
            stock = self.env['product.template'].search(domain)
            for prod in stock:

                # verifico si el producto tiene mas de un proveedor
                if len(prod.seller_ids) > 1:
                    # de los proveedores me quedo con el mas nuevo
                    ref = {'date': '0000-00-00', 'id': 0}
                    for seller in prod.seller_ids:
                        if seller.date_start > ref['date']:
                            ref['date'] = seller.date_start
                            ref['id'] = seller.name.id

                    # si el mas nuevo no coincide con el rec salteo y voy
                    # al siguiente
                    if ref['id'] != rec.vendor_id.id:
                        continue

                stock_valuation += prod.virtual_available * prod.final_price
                count += prod.virtual_available

            rec.write({
                'total_payable': rec.vendor_id.debit,
                'stock_valuation': stock_valuation,
                'count': count,
                'updated': fields.datetime.now() + timedelta(days=1)
            })
