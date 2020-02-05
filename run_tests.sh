#!/usr/bin/env bash
# correr test suite para iomaq

oe -Q bi_sales_iomaq -c iomaq -d iomaq_test
oe -Q product_autoload -c iomaq -d iomaq_test
oe -Q product_currency_fix -c iomaq -d iomaq_test
oe -Q product_upload -c iomaq -d iomaq_test