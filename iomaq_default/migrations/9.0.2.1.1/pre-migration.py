# For copyright and license notices, see __manifest__.py file in module root
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    import wdb;wdb.set_trace()

    loc = env['stock.location']
    loc._parent_store_compute()
