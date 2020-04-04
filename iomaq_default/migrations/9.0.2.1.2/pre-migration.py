# -*- coding: utf-8 -*-
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Necesito q cambies el nombre del vendedor de la factura de Omint
    # nro 5433 emitida en el dia de ayer, donde dice Manuel Rodriguez,
    # tiene q decir Silvana x favor
    invoice = env['account.invoice'].search([('id', '=', 13433)])
    invoice.user_id = 44
