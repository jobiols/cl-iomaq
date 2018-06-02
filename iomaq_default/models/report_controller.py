# -*- coding: utf-8 -*-
from openerp.addons.web.http import route
from openerp.addons import report


class ReportControllerDerived(report.controllers.main.ReportController):
    """ En point_of_sale cuando hacemos una factura sale la de aeroo en lugar
        de salir la odoo default
    """

    # TODO mover esto a un modulo para que se pueda reusar.

    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):

        # le cambiamos el reporte para que salga el de aeroo
        data = data.replace('point_of_sale.report_invoice',
                            'aeroo_report_ar_einvoice')

        ret = super(ReportControllerDerived, self).report_download(data, token)
        return ret
