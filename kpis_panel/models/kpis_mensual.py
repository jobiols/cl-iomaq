# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import models, fields, api
import datetime
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

RECEIVABLE_ID = 1
PAYABLE_ID = 2


class Kpis_mensual(models.Model):
    _name = 'kpis_panel.kpis_mensual'

    @api.multi
    def _get_company_currency(self):
        for rec in self:
            rec.currency_id = rec.env.user.company_id.currency_id

    date = fields.Date(
        name='Fecha',
        help='Fecha en la que se calculan los valores'
    )
    stock_value = fields.Monetary(
        name='Valuacion de Stock',
        help='Valuacion de stock al precio de compra'
    )
    payable = fields.Monetary(
        name='Deuda con proveedores',
        help='Es el balance de las cuentas de tipo "A Pagar" '
    )
    receivable = fields.Monetary(
        name='Deuda de los clientes',
        help='Es el balance de las cuentas de tipo "A Cobrar" '
    )
    currency_id = fields.Many2one(
        'res.currency',
        compute='_get_company_currency',
        readonly=True,
        string="Currency",
        help='Utility field to express amount currency'
    )

    @api.model
    def run(self):
        _logger.info('updating mensual kpi')

        # fecha del dia de hoy
        date = datetime.date.today()
        # sumamos un dia
        tomorrow = date + relativedelta(days=1)
        # si no cambia el mes, no es el ultimo dia, entonces terminamos
        if date.month == tomorrow.month:
            return

        # obtener el total de stock valuado al costo para las ubicaciones
        # que dependen de WH, (Outlet y Existencias).
        quant_obj = self.env['stock.quant']
        domain = [('location_id.location_id.name', '=', 'WH')]
        quants = quant_obj.search(domain)
        stock_value = 0;
        for q in quants:
            stock_value += q.qty * q.cost

        trial_balance = self.env['report.account.report_trialbalance']
        trial = trial_balance.with_context(date_to=date.strftime('%Y-%m-%d'))
        payable = receivable = 0

        # obtener el total de las cuentas a pagar.
        domain = [('user_type_id', '=', PAYABLE_ID)]
        payable_ids = self.env['account.account'].search(domain)
        account_res = trial._get_accounts(payable_ids, 'movement')
        for account in account_res:
            payable += account['balance']

        # obtener el total de las cuentas a cobrar.
        domain = [('user_type_id', '=', RECEIVABLE_ID)]
        receivable_ids = self.env['account.account'].search(domain)
        account_res = trial._get_accounts(receivable_ids, 'movement')
        for account in account_res:
            receivable += account['balance']

        self.create({'date': date,
                     'stock_value': stock_value,
                     'payable': payable,
                     'receivable': receivable
                     })
