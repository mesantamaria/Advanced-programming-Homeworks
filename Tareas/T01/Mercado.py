from decimal import Decimal as d
from User import *


class Mercado:
    def __init__(self, ticker):
        self.ticker = ticker
        self.divisa_compraventa = ticker[0:3]  # son simbolos
        self.moneda_de_cambio = ticker[3:]  # son simbolos
        self.orders = []
        self.asks = []
        self.bids = []
        self.asks_activos = []
        self.bids_activos = []
        self.tasa = d("0.1")
        self.resto_tasa = d("1") - d("0.1")  # acceso rapido
        self.comisiones = {self.divisa_compraventa: "0",
                           self.moneda_de_cambio: "0"}

    def numero_de_ordenes(self):
        cantidad_ordenes = len(self.orders)
        return cantidad_ordenes

    def spread_actual(self):
        lista_precios_venta = []
        lista_precios_compra = []
        for venta in self.asks_activos:
            lista_precios_venta.append(float(venta.moneda_de_cambio))
        for compra in self.bids_activos:
            lista_precios_compra.append(float(compra.moneda_de_cambio))
        if len(lista_precios_venta) == 0 or len(lista_precios_compra) == 0:
            spread = 0
            print("No hay suficientes compras y ventas para calcular un "
                  "spread.")
        else:
            spread = min(lista_precios_venta) - max(lista_precios_compra)
        return spread

    def ask_best(self):
        lista_precios_venta = []
        for venta in self.asks_activos:
            lista_precios_venta.append(float(venta.moneda_de_cambio))
        if len(lista_precios_venta) == 0:
            ask_best = 0
            print("No hay asks activos en el mercado para calcular un best.")
        else:
            ask_best = min(lista_precios_venta)
        return ask_best

    def bid_best(self):
        lista_precios_compra = []
        for compra in self.bids_activos:
            lista_precios_compra.append(float(compra.moneda_de_cambio))
        if len(lista_precios_compra) == 0:
            bid_best = 0
            print("No hay bids activos en el mercado para calcular un best.")
        else:
            bid_best = max(lista_precios_compra)
        return bid_best

    def volumen_acumulado_asks(self):
        currency_compraventa = 0
        moneda_de_cambio = 0
        for venta in self.asks:
            currency_compraventa += float(venta.divisa_venta)
            moneda_de_cambio += float(venta.moneda_de_cambio) * \
                                float(venta.divisa_venta)
        return currency_compraventa, moneda_de_cambio

    def volumen_acumulado_bids(self):
        currency_compraventa = 0
        moneda_de_cambio = 0
        for compra in self.bids:
            currency_compraventa += float(compra.divisa_compra)
            moneda_de_cambio += float(compra.moneda_de_cambio) *\
                                float(compra.divisa_compra)
        return currency_compraventa, moneda_de_cambio

    def desplegar_informacion(self):
        print("MERCADO: ", self.ticker)
        print("Numero de ordenes: ", self.numero_de_ordenes())
        print("Spread actual: ", self.spread_actual())
        print("Volumen acumulado de asks: ", self.divisa_compraventa,
              self.volumen_acumulado_asks()[0], "|",
              self.moneda_de_cambio, self.volumen_acumulado_asks()[1])
        print("Volumen acumulado de bids: ", self.divisa_compraventa,
              self.volumen_acumulado_bids()[0], "|",
              self.moneda_de_cambio, self.volumen_acumulado_bids()[1])
        print("Ask best: ", self.ask_best())
        print("Bid best: ", self.bid_best(), "\n")

    def determinar_tasa(self, usuario):
        if isinstance(usuario, Investor):
            resto_tasa = d("1") - self.tasa / d("2")
            return resto_tasa
        else:
            return self.resto_tasa


class Moneda:
    def __init__(self, simbolo, nombre):
        self.simbolo = simbolo
        self.nombre = nombre

    def __str__(self):
        imprimir = "Simbolo moneda: " + self.simbolo + " | " + \
                   "Nombre moneda: " + self.nombre
        return imprimir
