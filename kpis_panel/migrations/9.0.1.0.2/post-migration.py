# -*- coding: utf-8 -*-
# For copyright and license notices, see __manifest__.py file in module root


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO kpis_panel_kpis_mensual (date)
        VALUES('2020-01-31')
        """)

    cr.execute(
        """
            UPDATE kpis_panel_kpis_mensual
            SET stock_value_purchase_historic = 18539125.15
            WHERE date = '2020-01-31';

            UPDATE kpis_panel_kpis_mensual
            SET stock_value_purchase = 31825696.52
            WHERE date = '2020-01-31';

            UPDATE kpis_panel_kpis_mensual
            SET stock_value_sell = 43610154.12
            WHERE date = '2020-01-31';

            UPDATE kpis_panel_kpis_mensual
            SET receivable = 6929238.10
            WHERE date = '2020-01-31';

            UPDATE kpis_panel_kpis_mensual
            SET payable = -33713711.19
            WHERE date = '2020-01-31';
        """)
