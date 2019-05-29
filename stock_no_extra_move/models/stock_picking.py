# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _create_extra_moves(self, picking):
        if not self.env.user.has_group(
            'stock_no_extra_move.group_can_increase_quantity'):
            raise UserError(
                _('Se ha bloqueado un intento de transferir cantidades '
                  'mayores a las definidas en la orden de venta, esto esta '
                  'prohibido. '
                  'Por favor verifique que tiene suficiente stock para '
                  'procesar el pedido. ')
            )
        return super(StockPicking, self)._create_extra_moves(picking)
