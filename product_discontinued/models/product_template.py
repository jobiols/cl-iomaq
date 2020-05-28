from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    discontinued = fields.Boolean(
        string='Discontinuado'
    )
