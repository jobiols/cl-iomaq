# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division


class FakeStock(object):
    def __init__(self):
        self._stock = []

    def append(self, quant):
        self._stock.append(quant)

    def push(self, qty, price):
        """ Mete un quant con cantidad y precio
        """
        self._stock.append({'qty': qty,
                            'price': price})

    def pop(self, qty):
        """ Saca qty productos ajustndo los quants y devolviendo el precio
        """
        num = 0
        # calcular cuantos quants estan afectados, habra que quitar
        # num -1 y corregir o no el ultimo
        for quant in self._stock:
            num += 1
            if self.qty(n=num) >= qty:
                break

        # obtener la cantidad de producto que hay en los num-1 quants
        quitados = self.qty(n=num - 1)

        # mover los num-1 quants a out
        out = FakeStock()
        for x in range(0, num - 1):
            q = self._stock.pop(0)
            out.append(q)

        # obtener la cantidad de producto a corregir en el ultimo quant
        corregir = qty - quitados

        # apuntar al ultimo
        quant = self._stock[0]

        # corregir la cantidad en este quant
        quant['qty'] -= corregir

        # meter el pedazo de quant en out si es que no es cero la cantidad
        # y con el mismo precio
        if corregir:
            out.push(corregir, quant['price'])

        # en el caso de que la correccion me lleve a un quant en cero lo mato
        if quant['qty'] == 0:
            self._stock.pop(0)

        return out._price()

    def qty(self, n=-1):
        """ Devuelve la cantidad en los n quants primeros para salir si es
            False los suma todos
        """
        if n == 0:
            return 0
        qty = 0
        for e in self._stock:
            qty += e['qty']
            if n != -1:
                n -= 1
            if n >= 0 and n == 0:
                return qty
        return qty

    def _price(self, n=-1):
        """ Devuelve el promedio ponderado del precio de los n quants primeros
            para salir.
        """
        price = qty = 0
        for e in self._stock:
            price += e['price'] * e['qty']
            qty += e['qty']

            if n:
                n -= 1
            if n >= 0 and n == 0:
                return price / qty if qty else 0

        return price / qty if qty else 0
