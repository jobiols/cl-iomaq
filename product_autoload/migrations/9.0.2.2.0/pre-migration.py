# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

def migrate(cr, version):
    """ Populate margin for all prods.
    """

    cr.execute(
        """
            UPDATE product_template
            SET sale_delay = 0
        """)
