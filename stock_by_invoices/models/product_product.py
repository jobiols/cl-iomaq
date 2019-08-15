# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root

from openerp import api, models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_by_invoices = fields.Float(
        string='Stock x Facturas',
        compute="_compute_stock_by_invoices"
    )

    @api.multi
    def _compute_stock_by_invoices(self):
        for rec in self:
            if rec.default_code:

                self.env.cr.execute("""
                    SELECT
                      ai.type, sum(quantity)
                    FROM account_invoice_line ail
                    JOIN product_product pp
                      ON pp.id = ail.product_id
                    JOIN account_invoice ai
                      ON ai.id = ail.invoice_id
                    GROUP BY pp.default_code, ai.type
                      HAVING  pp.default_code = %s;
                """, (rec.default_code,))
                stock = self.env.cr.fetchall()
                ret = {}
                for type in stock:
                    ret[type[0]] = type[1]

                rec.stock_by_invoices = \
                    + (ret.get('in_invoice', 0) - ret.get('in_refund', 0)) \
                    - (ret.get('out_invoice', 0) - ret.get('out_refund', 0))
