# -*- coding: utf-8 -*-

from openerp import models, api, fields
import csv


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    comment = fields.Text('Additional Information', readonly=False)

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

        import re

        prod_obj = self.env['product.product']
        prods = prod_obj.search([('virtual_available', '!=', 0),
                                 ('type', '=', 'product')])

        with open('/opt/odoo/data/stock.csv', 'w') as csv_file:
            fieldnames = ['Codigo', 'Descripcion', 'Proveedor', 'En Mano',
                          'Previsto', 'Factura', 'Costo Hoy', 'Costo Compra']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames,
                                    quotechar='"',
                                    quoting=csv.QUOTE_ALL)
            writer.writeheader()

            for prod in prods:
                vendor = prod.seller_ids[0].name.ref if prod.seller_ids else ''
                writer.writerow({
                    'Codigo': prod.default_code,
                    'Descripcion': re.sub('^a-zA-Z0-9_', '', prod.name),
                    'Proveedor': vendor,
                    'En Mano': prod.qty_available,
                    'Previsto': prod.virtual_available,
                    'Factura': stock.get(prod.default_code, 'S/Fact'),
                    'Costo Hoy': prod.bulonfer_cost,
                    'Costo Compra': prod.standard_product_price
                })
