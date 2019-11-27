# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division
import logging

_logger = logging.getLogger(__name__)


class CommonMapper(object):
    @staticmethod
    def check_string(field, value):
        try:
            value.decode('utf-8')
        except Exception as ex:
            _logger.error('Error reading data.csv: Can not convert Field: '
                          '%s Value: %s to unicode, '
                          '%s' % (field, value, ex.message))
            raise
        return value

    @staticmethod
    def check_numeric(field, value):
        try:
            ret = int(value)
            return ret
        except ValueError as ex:
            _logger.error('Error reading data.csv: '
                          'Can not convert Field: %s Value: %s to number, '
                          '%s' % (field, value, ex.message))
            raise


MAP_DEFAULT_CODE = 0
MAP_NAME = 1
MAP_DESCRIPTION_SALE = 2
MAP_STANDARD_PRICE = 3
MAP_UPV = 4
MAP_WEIGHT = 5
MAP_VOLUME = 6
MAP_WHOLESALER_BULK = 7
MAP_RETAIL_BULK = 8
MAP_IMAGE_NAME = 9
MAP_WARRANTY = 10
MAP_IVA = 11
MAP_ITEM_CODE = 12
MAP_WRITE_DATE = 13
MAP_LEN = 14


class ProductMapper(CommonMapper):
    def __init__(self, line, image_path=False, vendor_ref=False):

        if len(line) != MAP_LEN:
            raise Exception('data.csv len is {} '
                            'must be {}'.format(len(line), MAP_LEN))
        self._vendor_ref = vendor_ref
        self._image_path = image_path
        self._image = False

        self._default_code = False
        self._name = False
        self._description_sale = False
        self._bulonfer_cost = 0
        self._upv = 0
        self._weight = 0
        self._volume = 0
        self._wholesaler_bulk = 0
        self._retail_bulk = 0
        self._image_name = False
        self._warranty = 0
        self._iva = 0
        self._item_code = False
        self._write_date = False
        self._invalidate_category = True

        self.default_code = line[MAP_DEFAULT_CODE]
        self.name = line[MAP_NAME]
        self.description_sale = line[MAP_DESCRIPTION_SALE]
        self.upv = line[MAP_UPV]
        self.bulonfer_cost = line[MAP_STANDARD_PRICE]
        self.bulonfer_cost /= self.upv
        self.weight = line[MAP_WEIGHT]
        self.volume = line[MAP_VOLUME]
        self.wholesaler_bulk = line[MAP_WHOLESALER_BULK]
        self.retail_bulk = line[MAP_RETAIL_BULK]
        self.image_name = line[MAP_IMAGE_NAME]
        self.warranty = line[MAP_WARRANTY]
        self.iva = line[MAP_IVA]
        self.item_code = line[MAP_ITEM_CODE]
        self.write_date = line[MAP_WRITE_DATE]

    def values(self, create=False):
        ret = dict()
        if create:
            ret['default_code'] = self.default_code
        ret['name'] = self.name
        ret['description_sale'] = self.description_sale
        ret['upv'] = self.upv
        ret['weight'] = self.weight
        ret['volume'] = self.volume
        ret['wholesaler_bulk'] = self.wholesaler_bulk
        ret['retail_bulk'] = self.retail_bulk
        ret['warranty'] = self.warranty
        ret['write_date'] = self.write_date
        ret['item_code'] = self.item_code
        ret['invalidate_category'] = self._invalidate_category
        if self._image:
            ret['image'] = self._image

        # agregar valores por defecto
        ret.update(self.default_values())
        return ret

    @staticmethod
    def default_values():
        return {
            'type': 'product',
            'invoice_policy': 'order',
            'purchase_method': 'purchase'
        }

    def execute(self, env):
        """ Este es el corazon del proceso de replicacion, si encuentra el
            producto en la bd lo actualiza si no lo encuentra lo crea.
        """

        def choose_tax(tax_sale):
            for tax in tax_sale:
                if tax.amount != 0:
                    # si no es cero es ese
                    return tax.id
                else:
                    # si es iva cero busco que sea exento
                    if tax.tax_group_id.afip_code == 2:
                        return tax.id

        # no permitir que modifique los 996.
        if self.default_code[0:4] == '996.':
            return []

        product_obj = env['product.template']
        prod = product_obj.search([('default_code', '=', self.default_code)])

        if prod:
            prod.write(self.values())
            stats = ['prod_processed']
            _logger.info('Updating product %s' % self.default_code)
        else:
            prod = product_obj.create(self.values(create=True))
            stats = ['prod_created']
            _logger.info('Creating product %s' % self.default_code)

        prod.set_prices(self.bulonfer_cost, self._vendor_ref,
                        date=self.write_date, min_qty=self.wholesaler_bulk,
                        vendors_code=self.default_code)
        prod.set_invoice_cost()

        tax_obj = env['account.tax']

        # actualiza IVA ventas
        tax_sale = tax_obj.search([('amount', '=', self.iva),
                                   ('tax_group_id.tax', '=', 'vat'),
                                   ('type_tax_use', '=', 'sale')])
        if not tax_sale:
            raise Exception('Product %s needs Customer Tax %s (IVA Sales)'
                            ' not found in Accounting' %
                            (self.default_code, self.iva))
        # analizando el iva
        tax = choose_tax(tax_sale)

        # esto reemplaza todos los registros por el tax que es un id
        prod.taxes_id = [(6, 0, [tax])]

        # actualiza iva compras
        tax_purchase = tax_obj.search([('amount', '=', self.iva),
                                       ('tax_group_id.tax', '=', 'vat'),
                                       ('type_tax_use', '=', 'purchase')])
        if not tax_purchase:
            raise Exception('Product %s needs Customer Tax %s (IVA Purchases)'
                            ' not found in Accounting' %
                            (self.default_code, self.iva))

        # analizando el iva
        tax = choose_tax(tax_purchase)

        # esto reemplaza todos los registros por el tax que es un id
        prod.supplier_taxes_id = [(6, 0, [tax])]

        # linkear los barcodes
        prodcode_obj = env['product_autoload.productcode']
        barcode_obj = env['product.barcode']

        recs = prodcode_obj.search([('product_code', '=', prod.default_code)])
        for rec in recs:
            _logger.info('Linking barcode %s' % rec.barcode)
            stats += barcode_obj.add_barcode(prod, rec.barcode)
        return stats

    @staticmethod
    def check_currency(field, value):
        try:
            ret = float(value)
            return ret
        except ValueError as ex:
            _logger.error('Error reading data.csv: '
                          'Can not convert Field: %s Value: %s to currency, '
                          '%s' % (field, value, ex.message))
            raise

    @staticmethod
    def check_float(field, value):
        try:
            ret = float(value)
            return ret
        except ValueError as ex:
            _logger.error('Error reading data.csv: '
                          'Can not convert Field: %s Value: %s to float, '
                          '%s' % (field, value, ex.message))
            raise

    def slugify(self, field, value):
        ret = self.check_string(field, value)
        ret.replace('/', '')
        return ret

    @property
    def default_code(self):
        return self._default_code

    @default_code.setter
    def default_code(self, value):
        self._default_code = self.check_string('default_code', value)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value:
            self._name = self.check_string('name', value)

    @property
    def description_sale(self):
        return self._description_sale

    @description_sale.setter
    def description_sale(self, value):
        if value:
            self._description_sale = self.check_string('description_sale',
                                                       value)

    @property
    def upv(self):
        return self._upv

    @upv.setter
    def upv(self, value):
        if value:
            self._upv = self.check_numeric('upv', value)

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        if value:
            self._weight = self.check_float('weight', value)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if value:
            self._volume = self.check_float('volume', value)

    @property
    def wholesaler_bulk(self):
        return self._wholesaler_bulk

    @wholesaler_bulk.setter
    def wholesaler_bulk(self, value):
        self._wholesaler_bulk = self.check_numeric('wholesaler_bulk', value)

    @property
    def retail_bulk(self):
        return self._retail_bulk

    @retail_bulk.setter
    def retail_bulk(self, value):
        self._retail_bulk = self.check_numeric('retail_bulk', value)

    @property
    def bulonfer_cost(self):
        return self._bulonfer_cost

    @bulonfer_cost.setter
    def bulonfer_cost(self, value):
        if value:
            self._bulonfer_cost = self.check_currency('bulonfer_cost', value)

    @property
    def image_name(self):
        return self._image_name

    @image_name.setter
    def image_name(self, value):
        if value:
            self._image_name = self.slugify('image_name', value)
            # cargar la imagen
            try:
                with open(self._image_path + self._image_name,
                          'rb') as img_file:
                    self._image = img_file.read().encode('base64')
            except IOError as ex:
                logging.error('{} {}'.format(ex.filename, ex.strerror))

    @property
    def iva(self):
        return self._iva

    @iva.setter
    def iva(self, value):
        if value:
            self._iva = self.check_float('iva', value)

    @property
    def warranty(self):
        return self._warranty

    @warranty.setter
    def warranty(self, value):
        if value:
            self._warranty = self.check_float('warranty', value)

    @property
    def item_code(self):
        return self._item_code

    @item_code.setter
    def item_code(self, value):
        self._item_code = self.check_string('Item Code', value)
