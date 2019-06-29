# -*- coding: utf-8 -*-

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    print 'calculando stock'

    @api.model
    def compute_stock(self):

        self.env.cr.execute("""
  SELECT
    pp.default_code,
    ai.type,
    sum(ail.quantity) as qty
  FROM account_invoice_line ail
    JOIN product_product pp
      ON pp.id = ail.product_id
    JOIN account_invoice ai
      ON ai.id = ail.invoice_id
  WHERE ai.state <> 'draft'
  GROUP BY type, default_code
        """)

        import re

        stock = {}
        r = self.env.cr.fetchone()
        while r is not None:

            default_code = r[0]
            type = r[1]
            if type in ['in_invoice', 'out_refund']:
                qty = r[2]
            if type in ['out_invoice', 'in_refund']:
                qty = -r[2]

            if not default_code in stock:
                stock[default_code] = qty
            else:
                stock[default_code] += qty
            r = self.env.cr.fetchone()

        print 'buscando productos'

        prod_obj = self.env['product.product']
        prods = prod_obj.search([('virtual_available', '!=', 0)])

        for prod in prods:

            print '"%s","%s","%s","%s","%s"' % (
                prod.default_code,
                re.sub('^a-zA-Z0-9_', '', prod.name),
                prod.qty_available,
                prod.virtual_available,
                stock.get(prod.default_code, 'S/Fact'))
