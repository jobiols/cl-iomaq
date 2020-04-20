# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class CheckPrices(models.TransientModel):
    _name = "product_autoload.check_prices"

    global_discount = fields.Float(
        help="Global discount % from Bulonfer",
        default=25.00,
        digits=dp.get_precision('Discount')
    )

    @api.multi
    def apply_discount(self):
        """ Calcula el precio bulonfer.
            En cada linea de la factura de bulonfer esta el precio del
            producto y un descuento por linea, luego hay un descuento global
            que se hace con una linea de descuento por cada tipo de IVA.

            Al tocar el boton Calcular Precios se lanza este wizard que primero
            consulta el descuento global y despues calcula el precio que tiene
            que aparecer en cada linea de la factura Bulonfer, para verificar
            que esta todo bien. (ese precio es mayor al precio iomaq a causa
            del descuento global)
        """
        for rec in self:
            po_id = self._context['purchase_order_id']
            purchase_order_obj = self.env['purchase.order']
            po = purchase_order_obj.search([('id', '=', po_id)])
            gdisc = rec.global_discount / 100
            for pol in po.order_line:
                ldisc = pol.discount / 100
                _ = (1-gdisc) * (1-ldisc)
                if pol.price_unit:
                    pol.bprice = pol.price_unit / _
                else:
                    pol.price_unit = pol.bprice * _
