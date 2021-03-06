# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

{
    'name': 'Stock Transfer Security',
    'version': '9.0.0.0.0',
    'category': 'Tools',
    'summary': "Agrega permisos para la transferencia de productos",
    'author': "jeo Software",
    'website': 'http://github.com/jobiols/cl-iomaq',
    'license': 'AGPL-3',
    "development_status": "Production/Stable",
    'depends': [
        'stock',
        'sale',
        'purchase'
    ],
    'data': [
        'security/security.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml'
    ],
    'installable': True,
    'application': False,
}
