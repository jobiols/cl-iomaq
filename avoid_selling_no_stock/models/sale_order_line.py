# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root
from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.exceptions import UserError
from datetime import datetime, timedelta
from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        #import wdb;wdb.set_trace()
        print '------------------------------------------------------'

        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.env['product.uom']._compute_qty_obj(self.product_uom, self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:

                    warning_mess = {
                        'title': _('You can not sell this quantity!'),
                        'message' : _('00You plan to sell %.2f %s but you only have %.2f %s available!\nThe stock on hand is %.2f %s.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
                    }
                    raise ValidationError(warning_mess['message'])

                    #return {'warning': warning_mess}
        return {}

    @api.multi
    def write(self, vals):
        """ Sobreescribe el write y no permite escribir la linea si es que no
            hay stock
        """
        #import wdb;wdb.set_trace()
        print '-=================================================================='
        print '-=================================================================='

        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.env['product.uom']._compute_qty_obj(self.product_uom, self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                if not is_available:

                    warning_mess = {
                        'title': _('You can not sell this quantity!'),
                        'message' : _('You plan to sell %.2f %s but you only have %.2f %s available!\nThe stock on hand is %.2f %s.') % \
                            (self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
                    }
                    raise UserError(warning_mess['message'])
                    return False

                return super(SaleOrderLine, self).write(vals)
