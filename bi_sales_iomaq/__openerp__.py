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
    'name': 'Sales Business Intelligence Report',
    'version': '9.0.0.7.0',
    'license': 'AGPL-3',
    'category': 'Tools',
    'summary': 'Custom BI Sales Report',
    'author': 'jeo Software',
    'depends': [
        'account'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/invoice_analysis.xml',
        'views/product_view.xml',
        'views/brand_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
}
