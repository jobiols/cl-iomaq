# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """ Populate invoice_cost.
    """

    products = env['product.template'].search([])
    for product in products:
        product.set_invoice_cost()
