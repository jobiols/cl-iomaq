# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#    Copyright (C) 2016  jeo Software  (http://www.jeosoft.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# -----------------------------------------------------------------------------
{
    'name': 'Iomaq',
    'version': '9.0.2.1.0',
    'license': 'Other OSI approved licence',
    'category': 'Tools',
    'summary': 'Customización IOMAQ SA',
    'author': 'jeo Software',
    'depends': [
        'avoid_selling_no_stock',   # evitar que se venda con stock negativo
        'support_branding_jeosoft',

        # aplicaciones instaladas
        'sale', 'l10n_ar_aeroo_sale',  # ventas
        'purchase', 'l10n_ar_aeroo_purchase',  # compras
        'account_accountant',  # permisos para contabilidad
        'l10n_ar_aeroo_stock',

        'product_currency_fix',  # fix para que ande con inventario permanente
        'stock_picking_auto',  # Automatic picking when Invoice is validated.
        'product_unique',
        'account_reconciliation_menu',  # agrega boton en partner
        'product_multi_barcode',
        'base_state_active',  # Deactivate US States
        'account_fix',  # Account Fixes
        'account_invoice_tax_wizard',  # add manual taxes on invoices
        'account_invoice_global_discount',  # descuentos en facturas de compra
        'web_export_view',  # exportar vistas en excel
        'account_clean_cancelled_invoice_number',  # borrar fac canceladas
        'price_security',   # Quien ve el precio de costo
        'base_currency_inverse_rate',  # Ver TC al derecho
        'l10n_ar_currency_update',  # Actualizar tipo de cambio
        'sale_order_validity',  # imprimir validez del presupuesto
        'kpis_panel',  # muestra tablero de control
        'account_cash_report',  # reporte de cajas
        'product_prices_update',  # incrementos de precios porcentuales
        'product_autoload',  # replicacion bulonfer
        'simple_meli_publishing',  # publicar precios de mercadolibre
        'simple_meshops_publishing',
        'bi_sales_iomaq',  # custom bi report for sales
        'sale_global_discount',  # setea todos los descuentos de la SO
        'document_page',  # documentacion y ayuda
        'product_upload',  # cargar productos desde planilla excel
    ],

    'data': [
        'views/product_view.xml',
        'views/custom_reports.xml',  # por si hay que hacer custom reports
        'views/stock_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],

    'port': '8069',
    'repos': [
        {'usr': 'jobiols', 'repo': 'cl-iomaq', 'branch': '9.0'},
        {'usr': 'jobiols', 'repo': 'odoo-addons', 'branch': '9.0'},
        {'usr': 'Vauxoo', 'repo': 'addons-vauxoo', 'branch': '9.0'},

    ],
    'docker': [
        {'name': 'aeroo', 'usr': 'jobiols', 'img': 'aeroo-docs'},
        {'name': 'odoo', 'usr': 'jobiols', 'img': 'odoo-jeo', 'ver': '9.0'},
        {'name': 'postgres', 'usr': 'postgres', 'ver': '9.5'},
        {'name': 'nginx', 'usr': 'nginx', 'ver': 'latest'}
    ]
}
