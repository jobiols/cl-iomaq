# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

from openerp.osv import osv


class ProductPricelist(osv.osv):
    _inherit = 'product.pricelist'

    def _price_get_multi(self, cr, uid, pricelist, products_by_qty_by_partner,
        context=None):
        """ Sobreescribimos esto para aplicar un aumento o bonificacion cliente
        """

        ret = super(ProductPricelist, self)._price_get_multi(
            cr, uid, pricelist, products_by_qty_by_partner, context=None)

        # obtenemos el partner id
        id_partner = products_by_qty_by_partner[0][2]

        # obtenemos el partner
        partner_id = self.pool.get('res.partner').browse(cr, uid, id_partner)

        # obtenemos el product id
        id_product = products_by_qty_by_partner[0][0].id

        # recalculamos el precio por el factor loayalty
        ret[id_product] *= (1 + partner_id.loyalty / 100)

        return ret
