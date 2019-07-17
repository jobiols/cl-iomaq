# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root


def migrate(cr, version):
    cr.execute(
        """
            UPDATE kpis_panel_kpis_mensual
            SET stock_value_purchase_historic = 16375813.77
            WHERE date = '2019-05-31';

            UPDATE kpis_panel_kpis_mensual
            SET stock_value_purchase_historic = 16941319.76
            WHERE date = '2019-06-30';

            UPDATE kpis_panel_kpis_mensual
            SET stock_value_purchase = 26842336.77
            WHERE date = '2019-06-30';

            UPDATE kpis_panel_kpis_mensual
            SET stock_value_sell = 33163701.24
            WHERE date = '2019-06-30';
        """)
