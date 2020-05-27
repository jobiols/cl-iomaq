# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            delete from account_check
            where number = 8256
        """)
