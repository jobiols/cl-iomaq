# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class InventoryMultiMgrLine(models.Model):
    _name = 'inventory_multi.mgr.line'

    inventory_id = fields.Many2one(
        'inventory_multi.mgr',
        'Inventory',
        ondelete='cascade',
        select=True
    )
    product_qty = fields.Float(
        string='Cantidad real',
        digits_compute=dp.get_precision('Product Unit of Measure')
    )
    product_id = fields.Many2one(
        'product.product',
        select=True,
        string="Producto"
    )


class InventoryMultiMgr(models.Model):
    _name = 'inventory_multi.mgr'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            raise UserError(_('You must define a warehouse for the company: %s.') % (company_user.name,))

    name = fields.Char(
        string='Referencia del Inventario',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicacion de Inventario',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=_default_location_id
    )
    description = fields.Text(

    )
    date_from = fields.Datetime(
        string='Inicio de inventario',
        default=fields.Datetime.now,
        readonly=True
    )
    date_to = fields.Date(
        string='Fin de inventario',
        readonly=True
    )
    line_ids = fields.One2many(
        'inventory_multi.mgr.line',
        'inventory_id',
        string='Productos a inventariar',
        readonly=False,
        states={'done': [('readonly', True)]}
    )
    user_ids = fields.Many2many(
        'res.users',
        string='Usuarios que realizaran el inventario'
    )
    state = fields.Selection(
        [('draft', 'Borrador'),
         ('in_process', 'En Proceso'),
         ('done', 'Finalizado'),
         ('cancel', 'Cancelado')],
        default='draft',
        string='Estado'
    )

    @api.multi
    def prepare_inventory(self):
        for rec in self:
            rec.state = 'in_process'

    @api.multi
    def cancel_inventory(self):
        for rec in self:
            rec.state = 'cancel'


class InventoryMultiUsr(models.Model):
    _name = 'inventory_multi.usr'

    name = fields.Char(

    )
