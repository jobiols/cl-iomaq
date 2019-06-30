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
    'name': 'Sale order validity fix',
    'version': '9.0.0.0.0',
    'category': 'Tools',
    'summary': "Corrige un comportamiento de indeseado de sale_order_validity",
    'author': "jeo Software",
    'website': 'http://github.com/jobiols/cl-iomaq',
    'license': 'AGPL-3',
    'depends': [
        'sale_order_validity'
    ],
    'data': [
        'views/sale_order_view.xml'
    ],
    'installable': True,
    'application': False,
}
