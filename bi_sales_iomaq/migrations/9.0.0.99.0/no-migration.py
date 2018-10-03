# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """ Recalculate product margin
    """
    lines = env['account.invoice.line'].search([])
    for ail in lines:
        ail._compute_product_margin()
