# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#    Copyright (C) 2018  jeo Software  (http://www.jeosoft.com.ar)
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
    'name': 'Inteligencia de negocio para ventas',
    'version': '9.0.0.10.1',
    'license': 'AGPL-3',
    "development_status": "Production/Stable",
    'category': 'Tools',
    'summary': 'Customizacion de BI para IOMAQ',
    'author': 'jeo Software',
    'depends': [
        'account',
        'product_currency_fix'
    ],

    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/invoice_analysis.xml',
        'views/product_view.xml',
        'views/brand_view.xml',
        'views/partner_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
