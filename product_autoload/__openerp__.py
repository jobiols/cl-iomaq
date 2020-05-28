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
    'name': 'Product autoload',
    'version': '9.0.2.2.1',
    'license': 'AGPL-3',
    "development_status": "Production/Stable",
    'category': 'Tools',
    'summary': 'Carga automatica de productos',
    'author': 'jeo Software',
    'depends': [
        'l10n_ar_account',
        'stock',
        'sale',
        'purchase',
        'product_multi_barcode',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'views/settings_view.xml',
        'views/product_view.xml',
        'views/autoload_manager_view.xml',
        'views/purchase_view.xml',
        'wizard/check_prices_view.xml',
        'security/security.xml'
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
