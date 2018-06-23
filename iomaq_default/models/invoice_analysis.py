# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models
from openerp import tools


class AccountInvoiceLineReport(models.Model):
    _inherit = "account.invoice.line.report"

    # Agregamos dos campos al pivot
    # - *cost_unit* es el costo unitario en moneda de la compa~nia y sin iva
    #   calculado desde el costo del producto.
    #
    # - *margin* es el margen de contribucion entre cost_unit y price_unit

    price_unit = fields.Float(
        'Costo +IVA',
        group_operator="sum",
        readonly=True,
        help="Costo +IVA"
    )

    price_subtotal = fields.Float(
        'Subtotal C/descuento',
        readonly=True,
        group_operator="sum",
        help="Subtotal con descuento"
    )

    margin_unit = fields.Float(
        'Margin',
        group_operator="sum",
        readonly=True
    )

    def init(self, cr):

        tools.drop_view_if_exists(cr, 'account_invoice_line_report')
        cr.execute("""
        CREATE OR REPLACE VIEW account_invoice_line_report AS (
        SELECT
            "account_invoice_line"."id" AS "id",

            -- Total de la factura con iva ------------------------------------
            "account_invoice_line"."price_subtotal_signed" *
                (1 + "account_invoice_line"."product_iva")
            AS "amount_total",

            -- Costo +IVA -----------------------------------------------------
            -- (tapa el campo price_unit) El costo es el precio menos el margen
            -- o sea tengo el precio en la factura y lo multiplico por
            -- (1 - margen) del producto. Hago esto porque no tengo el costo
            -- a la fecha de la venta. y le sumo el IVA
            "account_invoice_line"."price_unit" *
                "account_invoice_line"."quantity" *
                    (1 - "account_invoice_line"."product_margin") *
                        (1 + "account_invoice_line"."product_iva") *
                            "account_invoice_line"."sign"
            AS "price_unit",

            -- Margen Precio menos costo, ojo que price_unit es el costo ------
            "account_invoice_line"."price_subtotal_signed" *
                ( 1 + "account_invoice_line"."product_iva")
                -
            "account_invoice_line"."price_unit" *
                "account_invoice_line"."quantity" *
                    (1 - "account_invoice_line"."product_margin") *
                        (1 + "account_invoice_line"."product_iva") *
                            "account_invoice_line"."sign"
            AS "margin_unit",

            "account_invoice_line"."discount"
            AS "discount",

            "account_invoice_line"."account_analytic_id"
            AS "account_analytic_id",

            "account_invoice_line"."quantity" *
                "account_invoice_line"."sign"
            As "quantity",

            -- Total de la factura sin iva, incluye el descuento de linea
            "account_invoice_line"."price_subtotal_signed"
            As "price_subtotal",

            "account_invoice_line"."price_unit" *
                "account_invoice_line"."quantity" *
                    "account_invoice_line"."sign"
            As "price_gross_subtotal",

            "account_invoice_line"."price_unit" *
                "account_invoice_line"."quantity" *
                    "account_invoice_line"."discount"/100 *
                        "account_invoice_line"."sign"
            As "discount_amount",

        "account_invoice_line"."partner_id" AS "partner_id",--n
        "account_invoice_line"."product_id" AS  "product_id", --n
        "account_invoice"."date_due" AS "date_due",
        COALESCE("account_invoice"."document_number",
        "account_invoice"."number") AS "number",
        "account_invoice"."journal_id" AS "journal_id",--n
        "account_invoice"."user_id" AS "user_id",--n
        "account_invoice"."company_id" AS "company_id",--n
        "account_invoice"."type" AS "type",
        "account_invoice"."state_id" AS "state_id",--n

        "account_invoice"."document_type_id" AS "document_type_id",
        "account_invoice"."state" AS "state",
        "account_invoice"."date" AS "date",
        "account_invoice"."date_invoice" AS "date_invoice",
        "product_product"."barcode" AS "barcode",
        "product_product"."name_template" AS "name_template",

        "product_template"."categ_id" as "product_category_id", --n
        "res_partner"."customer" AS "customer",
        "res_partner"."supplier" AS "supplier"

        FROM "account_invoice_line" "account_invoice_line"
        INNER JOIN "account_invoice" "account_invoice"
        ON ("account_invoice_line"."invoice_id" = "account_invoice"."id")
        LEFT JOIN "product_product" "product_product"
        ON ("account_invoice_line"."product_id" = "product_product"."id")
        INNER JOIN "res_partner" "res_partner"
        ON ("account_invoice"."partner_id" = "res_partner"."id")
        LEFT JOIN "product_template" "product_template"
        ON ("product_product"."product_tmpl_id" = "product_template"."id")
        -- INNER JOIN "public"."account_period" "account_period"
        -- ON ("account_invoice"."period_id" = "account_period"."id")
        ORDER BY number ASC
              )""")
