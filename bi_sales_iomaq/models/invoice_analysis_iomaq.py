# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models
from openerp import tools


class AccountInvoiceLineReportIomaq(models.Model):
    _name = "account.invoice.line.report.iomaq"
    _description = "Invoices Statistics"
    _auto = False

    price_total = fields.Float(
        'Price',
        readonly=True,
    )
    price_total_taxed = fields.Float(
        'Price +tax',
        readonly=True,
    )
    cost_total = fields.Float(
        'Cost',
        readonly=True,
    )
    cost_total_taxed = fields.Float(
        'Cost +tax',
        readonly=True,
    )
    margin_total = fields.Float(
        'Margin',
        readonly=True,
    )
    margin_total_taxed = fields.Float(
        'Margin +tax',
        readonly=True,
    )
    discount_total = fields.Float(
        'Discount',
        readonly=True
    )
    discount_total_taxed = fields.Float(
        'Discount +tax',
        readonly=True
    )
    quantity = fields.Float(
        'Quantity',
        readonly=True,
        group_operator="sum"
    )
    date_due = fields.Date(
        'Due Date',
        readonly=True
    )
    number = fields.Char(
        string='Number',
        size=128, readonly=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Done'),
        ('cancel', 'Cancelled')
    ],
        'Invoice State',
        readonly=True
    )
    document_type_id = fields.Many2one(
        'account.document.type',
        readonly=True
    )
    date = fields.Date(
        'Accounting Date',
        readonly=True
    )
    date_invoice = fields.Date(
        'Date Invoice',
        readonly=True
    )
    date_invoice_from = fields.Date(
        compute=lambda *a, **k: {}, method=True, string="Date Invoice from")
    date_invoice_to = fields.Date(
        compute=lambda *a, **k: {}, method=True, string="Date Invoice to")
    product_id = fields.Many2one(
        'product.product',
        'Product',
        readonly=True
    )
    name_template = fields.Char(
        string="Product by text",
        size=128,
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        readonly=True
    )
    customer = fields.Boolean(
        'Customer',
        help="Check this box if this contact is a customer.",
        readonly=True
    )
    supplier = fields.Boolean(
        'Supplier',
        help="Check this box if this contact is a supplier."
             " If it's not checked,"
             "purchase people will not see it when encoding a purchase order.",
        readonly=True)
    journal_id = fields.Many2one(
        'account.journal',
        'Journal',
        readonly=True
    )
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund'),
    ],
        'Type',
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users',
        'Salesman',
        readonly=True)
    state_id = fields.Many2one(
        'res.country.state',
        'State',
        readonly=True
    )
    product_category_id = fields.Many2one(
        'product.category',
        'Category',
        readonly=True
    )
    brand_id = fields.Many2one(
        'bi_sales_iomaq.brand',
        'Brand',
        readonly=True
    )
    vendor_id = fields.Many2one(
        'res.partner',
        'Vendor',
        readonly=True
    )
    _order = 'id'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_invoice_line_report_iomaq')
        cr.execute("""
        CREATE OR REPLACE VIEW account_invoice_line_report_iomaq AS (
        SELECT
        ail.id AS id,

        --- PRECIO TOTAL DE LA LINEA DE FACTURA SIN IVA
        --- Esto incluye los descuentos que hubiera en la linea
        ail.price_subtotal_signed AS price_total,

        --- PRECIO TOTAL DE LA LINEA DE FACTURA CON IVA
        --- Es el anterior mas IVA
        ail.price_subtotal_signed *
                (1 + ail.product_iva)
        AS price_total_taxed,

        --- COSTO TOTAL DE LA LINEA DE FACTURA SIN IVA
        --- Es el costo que tenia el producto cuando lo compre, no el costo
        --- actual, para encontrarlo multiplico el precio de la factura por
        --- (1 - margen)
        ail.price_subtotal_signed *
            (1 - ail.product_margin)
        AS cost_total,

        --- COSTO TOTAL DE LA LINEA DE FACTURA CON IVA
        --- Es el anterior mas iva
        ail.price_subtotal_signed *
            (1 - ail.product_margin) *
                (1 + ail.product_iva)
        AS cost_total_taxed,

        --- MARGEN TOTAL DE LA LINEA DE FACTURA SIN IVA
        --- Es la diferencia entre el precio de venta que se pone en la factura
        --- y el precio al que compramos el producto que se esta vendiendo
        --- calculado como precio * margen
        ail.price_subtotal_signed *
            ail.product_margin
        AS margin_total,

        --- MARGEN TOTAL DE LA LINEA DE FACTURA CON IVA
        --- Es el anterior mas el iva
        ail.price_subtotal_signed *
            ail.product_margin *
                (1 + ail.product_iva)
        AS margin_total_taxed,

        --- DISCOUNT TOTAL DE LA LINEA DE FACTURA SIN IVA
        ail.price_unit *
            ail.quantity *
                (ail.discount / 100) *
                    (-ail.sign)
        AS discount_total,

        --- DISCOUNT TOTAL DE LA LINEA DE FACTURA CON IVA
        ail.price_unit *
            ail.quantity *
                (ail.discount / 100) *
                    (1 + ail.product_iva) *
                        (-ail.sign)
        AS discount_total_taxed,

        --- CANTIDAD DE PRODUCTO EN LA LINEA DE FACTURA
        ail.quantity AS quantity,

        ail.partner_id AS partner_id,
        ail.product_id AS  product_id,
        ai.date_due AS date_due,

        COALESCE(ai.document_number, ai.number) AS number,

        ai.journal_id AS journal_id,

        ai.user_id AS user_id,

        ai.type AS type,

        ai.state_id AS state_id,

        ai.document_type_id AS document_type_id,

        ai.state AS state,

        ai.date AS date,

        ai.date_invoice AS date_invoice,

        pp.name_template AS name_template,

        pt.categ_id as product_category_id,

        rp.customer AS customer,

        rp.supplier AS supplier,

        pt.brand_id AS brand_id,

        ail.vendor_id AS vendor_id

        FROM account_invoice_line ail
        INNER JOIN account_invoice ai
        ON (ail.invoice_id = ai.id)

        LEFT JOIN product_product pp
        ON (ail.product_id = pp.id)

        INNER JOIN res_partner rp
        ON (ai.partner_id = rp.id)

        LEFT JOIN product_template pt
        ON (pp.product_tmpl_id = pt.id)

        ORDER BY number ASC
        )"""
                   )
