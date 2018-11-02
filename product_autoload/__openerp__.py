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
    'version': '9.0.2.1.0',
    'license': 'AGPL-3',
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
    'test': [
    ],
    'demo': [
        'data/demo_data.xml',
#   TODO ver como hacer para que no genere el errror de unused file
#        'data/section.csv',
#        'data/family.csv',
#        'data/productcode_changed.csv',
#        'data/productcode.csv',
#        'data/data.csv',
#        'data/item_changed.csv',
#        'data/item.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
