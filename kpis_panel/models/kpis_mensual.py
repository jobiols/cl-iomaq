# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from openerp import models, fields, api
import datetime
import time
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

RECEIVABLE_ID = 1
PAYABLE_ID = 2


class Kpis_mensual(models.Model):
    _name = 'kpis_panel.kpis_mensual'
    _order = 'date desc'

    @api.multi
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.env.user.company_id.currency_id

    date = fields.Date(
        name='Fecha',
        help='Fecha en la que se calculan los valores',
        readonly=True
    )
    stock_value_purchase_historic = fields.Monetary(
        string='Valuacion de Stock (compra historica)',
        help='Valuacion de stock al precio historico de compra. Es el precio '
             'que se pago al comprarlo.',
        readonly=True
    )
    stock_value_purchase = fields.Monetary(
        string='Valuacion de Stock (compra a la fecha)',
        help='Valuacion de stock al precio de compra. Es el precio de compra '
             'que tenia a la fecha de este registro',
        readonly=True
    )
    stock_value_sell = fields.Monetary(
        string='Valuacion de Stock (venta a la fecha)',
        help='Valuacion de stock al precio de venta, es el precio de venta '
             'que tenia a la fecha de este registro',
        readonly=True
    )

    payable = fields.Monetary(
        string='Deuda con proveedores',
        help='Es el balance de las cuentas de tipo "A Pagar" ',
        readonly=True
    )
    receivable = fields.Monetary(
        string='Deuda de los clientes',
        help='Es el balance de las cuentas de tipo "A Cobrar" ',
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_currency_id',
        string="Currency",
        help='Utility field to express amount currency',
        readonly=True
    )

    @api.model
    def run(self):
        """ Calcula los kpi mensuales, esto tarda unos cuatro minutos
        """
        # fecha del dia de hoy
        date = datetime.date.today()
        # para pruebas fecha del dia de la prueba
        # date = datetime.datetime.strptime('2020-01-31', '%Y-%m-%d')
        # sumamos un dia
        tomorrow = date + relativedelta(days=1)
        # si no cambia el mes, no es el ultimo dia, entonces terminamos
        if date.month == tomorrow.month:
            return

        _logger.info('updating mensual kpi')
        start_time = time.time()

        # obtener el total de stock valuado al costo de compra para las
        # ubicaciones que dependen de WH, (Outlet y Existencias).
        # no considero stock negativo
        # q.cost ya esta en la moneda de la compa~nia aunque el producto este
        # en dolares.
        quant_obj = self.env['stock.quant']
        domain = [('location_id.location_id.name', '=', 'WH')]
        quants = quant_obj.search(domain)
        stock_value_purchase_historic = 0
        for q in quants:
            if q.qty > 0:
                stock_value_purchase_historic += q.qty * q.cost

        # obtener el total de stock valuado al costo hoy
        # no considero stock negativo
        domain = [('virtual_available', '>', 0)]
        products = self.env['product.product'].search(domain)

        stock_value_purchase = 0
        stock_value_sell = 0
        for prod in products:
            cc = prod.company_id.currency_id
            pc = prod.currency_id
            cost = pc.compute(prod.bulonfer_cost, cc, round=False)
            price = pc.compute(prod.list_price, cc, round=False)
            stock_value_purchase += cost * prod.virtual_available
            stock_value_sell += price * prod.virtual_available

        # trial balance para calcular totales a pagar y a cobrar
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

        self.create(
            {'date': date,
             'stock_value_purchase_historic': stock_value_purchase_historic,
             'stock_value_purchase': stock_value_purchase,
             'stock_value_sell': stock_value_sell,
             'payable': payable,
             'receivable': receivable
             })

        elapsed_time = time.time() - start_time
        _logger.info('mensual kpi, execution time %s' % time.strftime(
            "%H:%M:%S", time.gmtime(elapsed_time)))
