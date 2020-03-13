# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "version": "9.0.1.0.0",
    "name": "Stock no extra move",
    "summary": "Prevent creation of extra moves in picking processing",
    "category": "Logistics",
    "website": "http://jeosoft.com.ar",
    "development_status": "Production/Stable",  # "Alpha|Beta|Production/Stable|Mature"
    "author": "jeosoft",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'stock',
    ],
    "data": [
        'security/groups.xml',
    ],
}
