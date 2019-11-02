# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


def migrate(cr, version):
    """ Ponerle el default a todos los partners
    """
    cr.execute(
        """
            UPDATE res_partner
            SET business_mode = 'standard';
        """)
