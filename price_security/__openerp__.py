# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
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
    'name': 'Price Security',
    'version': '9.0.1.4.1',
    'category': 'Sales Management',
    'author': 'ADHOC SA, Odoo Community Association (OCA), jeo Software',
    'website': 'http://www.jeosoft.com.ar/',
    'license': 'AGPL-3',
    "development_status": "Production/Stable",  # "Alpha|Beta|Production/Stable|Mature"
    'depends': [
        'sale',
        'stock',
        'product_autoload',
        'product_currency_fix'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users_view.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
        'views/invoice_view.xml',
        'views/partner_view.xml',
        'views/account_view.xml',
        'views/stock_view.xml'
    ],
    'installable': True,
}
