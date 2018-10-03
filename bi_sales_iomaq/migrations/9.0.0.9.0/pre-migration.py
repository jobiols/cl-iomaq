# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


def migrate(cr, version):
    cr.execute(
        """
            ALTER TABLE account_invoice_line
            DROP COLUMN product_margin CASCADE;
        """)
