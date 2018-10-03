# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


def migrate(cr, version):
    """ Populate margin for all prods.
    """

    cr.execute(
        """
            UPDATE product_template
            SET margin = 100 * (list_price / bulonfer_cost -1)
            WHERE list_price <> 0 AND bulonfer_cost <> 0
        """)