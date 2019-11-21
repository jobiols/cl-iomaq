# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import fields, models, api


class ProductBrand(models.Model):
    _name = "bi_sales_iomaq.brand"
    _description = "Establece las marcas de los productos"

    name = fields.Char(
        help='Brand name',
    )
    mask = fields.Char(
        help='Brand mask'
    )
    product_count = fields.Integer(
        compute='_compute_product_count',
        readonly=True
    )
    product_template_ids = fields.One2many(
        comodel_name='product.template',
        inverse_name='brand_id',
        string="Products",
        readonly=True
    )

    @api.multi
    @api.depends('product_template_ids')
    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_template_ids)

    @api.multi
    def check_mask(self):
        for rec in self:
            prod_obj = self.env['product.product']
            cr = prod_obj.env.cr
            cr.execute("SELECT id FROM product_product "
                       "WHERE default_code LIKE %s", (rec.mask,))

            pids = [x[0] for x in cr.fetchall()]
            prods = prod_obj.browse(pids)
            tids = [x.product_tmpl_id.id for x in prods]
            rec.product_template_ids = [(6, 0, tids)]
