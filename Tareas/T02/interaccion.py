import gui
import sys
from random import choice, randint
from piezas import *
from tablero import *
from jugadores import *


class MyInterface(gui.GameInterface):
    def __init__(self):
        self.a = 0
        self.contador_erroneas = 0
        self.juego_terminado = False
        self.piezas = ListaLigada()
        self.cantidad_piezas = cantidad_piezas  # key = Pieza(str)
        #  value = cantidad (int)
        for pieza, cantidad in self.cantidad_piezas.items():
            for i in range(0, cantidad):
                nueva_pieza = Pieza(pieza)
                if pieza == "CGGCGG" or pieza == "CRCCRC" or pieza == "CGGGCC":
                    nueva_pieza.ciudad_separada = True
                self.piezas.append(nueva_pieza)
        self.tablero_objeto = Tablero()
        self.tablero = self.tablero_objeto.elementos
        self.entidades = ListaLigada()
        self.mejor_posicion = None
        self.jugadores = Tupla(Jugador(1, "red"), Jugador(2, "blue"))
        self.jugador_actual = self.jugadores[0]  # jugador inicial
        primera = self.obtener_pieza_random()
        gui.nueva_pieza("red", primera.bordes)  # para poner la primera pieza
        i = randint(0, 7)
        j = randint(0, 7)
        gui.add_piece(i, j)
        self.tablero[Tupla(i, j)] = primera
        primera.posicion = Tupla(i, j)
        self.jugador_actual.movimientos.append(Tupla(i, j))
        self.jugador_actual.piezas.append(primera)
        # la primera pieza se asume como del jugador 1
        if "C" in primera.bordes:
            # esto se hace porque las ciudades se pueden formar con 1 pieza
            self.crear_ciudad(primera)
            if primera.ciudad_separada:
                self.crear_ciudad(primera)
        self.pieza_actual = self.obtener_pieza_random()
        gui.nueva_pieza("red", self.pieza_actual.bordes)
        # para poner la segunda pieza
        # variables para el historial
        self.hist_tableros = ListaLigada()
        self.hist_entidades = ListaLigada()
        self.hist_jugadores = ListaLigada()
        self.hist_piezas = ListaLigada()
        self.hist_turno_actual = ListaLigada()  # elem = (Jugador, pieza)

    def obtener_pieza_random(self):
        piezas_disponibles = ListaLigada()
        for pieza in self.piezas:
            if self.cantidad_piezas[pieza.bordes] > 0:
                piezas_disponibles.append(pieza)
        if len(piezas_disponibles) > 0:
            pieza_elegida = choice(self.piezas)
            # pieza_elegida = self.piezas[30]  # 30 para hacer ciudades chicas
            # con caminos, 82 ciudades largas, 113 caminos
            self.piezas.remove(pieza_elegida)
            self.cantidad_piezas[pieza_elegida.bordes] -= 1  # una pieza menos
        else:
            print("No quedan piezas")
        return pieza_elegida

    def otro_jugador(self):
        if self.jugador_actual == self.jugadores[0]:
            return self.jugadores[1]
        else:
            return self.jugadores[0]

    def cambiar_color(self, pieza, entidad_actual):
        # entidad donde esta la pieza
        otro_jugador = self.otro_jugador()
        otro_jugador.movimientos.remove(pieza.posicion)
        self.jugador_actual.movimientos.append(pieza.posicion)
        otro_jugador.piezas.remove(pieza)
        self.jugador_actual.piezas.append(pieza)
        i = pieza.posicion[0]
        j = pieza.posicion[1]
        gui.pop_piece(i, j)
        gui.nueva_pieza(self.jugador_actual.color, pieza.id)
        bordes_anteriores = pieza.bordes
        aux = pieza.id
        while aux != bordes_anteriores:
            gui.rotate_piece()
            aux = aux[-1] + aux[0:5]
            self.pieza_actual.rotar_izquierda()  # rotate la gira a la derecha
        gui.add_piece(i, j)
        # ahora tenemos que borrar la pieza de otras entidades si la contienen
        entidades_aux = otro_jugador.entidades
        for entidad in entidades_aux:
            if pieza in entidad.piezas and entidad != entidad_actual:
                if len(entidad.piezas) == 2 and entidad.tipo != "C":
                    self.entidades.remove(entidad)
                    otro_jugador.entidades.remove(entidad)
                elif len(entidad.piezas) >= 2 and entidad.tipo == "C":
                    entidad.piezas.remove(pieza)
                    self.crear_ciudad(pieza)
                elif len(entidad.piezas) == 1 and entidad.tipo == "C":
                    otro_jugador.entidades.remove(entidad)
                    self.jugador_actual.entidades.append(entidad)
                elif len(entidad.piezas) > 2:
                    entidad.piezas.remove(pieza)

        i = pieza.posicion[0]
        j = pieza.posicion[1]
        up, down, upright, upleft, dright, dleft = self.vecinos(i, j)
        self.generar_entidad2(pieza, self.pieza_actual, up, down,
                              upright, upleft, dright, dleft)

    def crear_ciudad(self, pieza):  # ciudades de una pieza
        cantidad_cities = 0
        cantidad_c = 0  # manejo de errores = no tener mas entidades que 'C's
        for borde in pieza.bordes:
            if borde == "C" and (pieza.id == "CGGCGG" or
                                 pieza.id == "CGGGCC"):
                cantidad_c += 1
        if cantidad_c == 0:
            cantidad_c = 1
            if pieza.id == "CRCCRC":
                cantidad_c = 2
        for entidad in self.entidades:
            if pieza in entidad.piezas and entidad.tipo == "C":
                cantidad_cities += 1
        if cantidad_cities < cantidad_c:
            nueva_entidad = Entidad("C")
            nueva_entidad.piezas.append(pieza)
            self.entidades.append(nueva_entidad)
            self.jugador_actual.entidades.append(nueva_entidad)

    def control_ciudades(self):
        for pieza in self.tablero.values():
            if pieza is not None:
                cantidad_cities = 0
                cantidad_c = 0  # manejo de errores = no tener mas entidades
                # que 'C's
                for borde in pieza.bordes:
                    if borde == "C" and (pieza.id == "CGGCGG" or
                                         pieza.id == "CGGGCC"):
                        cantidad_c += 1
                if cantidad_c == 0:
                    cantidad_c = 1
                    if pieza.id == "CRCCRC":
                        cantidad_c = 2

                entidades_controladas = ListaLigada()
                aux = ListaLigada()
                for entidad in self.entidades:
                    if pieza in entidad.piezas and entidad.tipo == "C":
                        cantidad_cities += 1
                        entidades_controladas.append(entidad)
                        aux.append(entidad)

                for entidad in aux:
                    if (len(entidad.piezas) == 1 and
                            cantidad_c < cantidad_cities):
                        for entidad2 in entidades_controladas:
                            if (entidad.piezas[0] in entidad2.piezas and
                                    entidad != entidad2):
                                self.entidades.remove(entidad)
                                otro_jugador = self.otro_jugador()
                                if entidad in self.jugador_actual.entidades:
                                    self.jugador_actual.entidades.\
                                        remove(entidad)
                                else:
                                    otro_jugador.entidades.remove(entidad)
                                cantidad_cities -= 1
                                break
                            if cantidad_cities <= cantidad_c:
                                break
                    if cantidad_cities <= cantidad_c:
                        break
        return cantidad_cities, cantidad_c

    def conectar_piezas(self, pieza_anterior, tipo):
        existe = False
        for entidad in self.entidades:
            if entidad.tipo == tipo and pieza_anterior in entidad.piezas:
                if self.pieza_actual not in entidad.piezas and \
                        not pieza_anterior.ciudad_separada and \
                        not pieza_anterior.bifurcacion:
                    # este if de tantas condiciones es por lo siguiente:
                    # primero queremos que la pieza anterior este dentro de
                    # alguna entidad existente. Luego la pieza anterior no
                    # puede ser una de los 2 tipos especificados, porque ahí
                    # su función es "cortar" la entidad, no continuarla.
                    existe = True
                    otro_jugador = self.otro_jugador()
                    if entidad not in self.jugador_actual.entidades and \
                            (entidad.tipo == "P" or entidad.tipo == "R"):
                        for pieza in entidad.piezas:
                            self.cambiar_color(pieza, entidad)
                        self.jugador_actual.entidades.append(entidad)
                        if entidad in otro_jugador.entidades:
                            otro_jugador.entidades.remove(entidad)
                        if "C" in self.pieza_actual.bordes:
                            self.crear_ciudad(self.pieza_actual)

                    elif entidad.tipo == "C":
                        for pieza in entidad.piezas:
                            if pieza in self.jugador_actual.piezas:
                                self.pieza_cerrada(pieza, self.jugador_actual,
                                                   True)
                            else:
                                self.pieza_cerrada(pieza, self.otro_jugador(),
                                                   True)
                            if pieza.cerrada:
                                entidad.completa = True
                            else:
                                entidad.completa = False
                                break
                        self.pieza_cerrada(self.pieza_actual,
                                           self.jugador_actual, True)
                        if entidad.completa and self.pieza_actual.cerrada:
                            for pieza in entidad.piezas:
                                if pieza not in self.jugador_actual.piezas:
                                    self.cambiar_color(pieza, entidad)
                            if entidad not in self.jugador_actual.entidades:
                                self.jugador_actual.entidades.append(entidad)
                                otro_jugador.entidades.remove(entidad)
                    entidad.piezas.append(self.pieza_actual)
                    break
                elif pieza_anterior.ciudad_separada and \
                        len(entidad.piezas) == 1:
                    otro_jugador = self.otro_jugador()
                    existe = True  # False
                    if pieza_anterior not in self.jugador_actual.piezas:
                        self.cambiar_color(pieza_anterior, None)
                    entidad.piezas.append(self.pieza_actual)
                    if entidad not in self.jugador_actual.entidades:
                        self.jugador_actual.entidades.append(entidad)
                        otro_jugador.entidades.remove(entidad)
                    if self.pieza_actual.ciudad_separada:
                        self.crear_ciudad(self.pieza_actual)

                    break
                elif pieza_anterior.bifurcacion:
                    existe = False
                    break
                else:
                    existe = True
        if not existe:
            nueva_entidad = Entidad(tipo)
            if pieza_anterior not in self.jugador_actual.piezas:
                self.cambiar_color(pieza_anterior, None)
            nueva_entidad.piezas.append(pieza_anterior)
            nueva_entidad.piezas.append(self.pieza_actual)
            self.entidades.append(nueva_entidad)
            self.jugador_actual.entidades.append(nueva_entidad)
            if tipo != "C" and "C" in self.pieza_actual.bordes:
                # esto se hace porque las ciudades se pueden formar con 1 pieza

                self.crear_ciudad(self.pieza_actual)
            if tipo != "C" and self.pieza_actual.ciudad_separada:
                self.crear_ciudad(self.pieza_actual)
            if tipo == "C" and self.pieza_actual.ciudad_separada:
                self.crear_ciudad(self.pieza_actual)
        aux = ListaLigada()
        for elem in self.jugador_actual.entidades:
            aux.append(elem)
        for entidad1 in self.jugador_actual.entidades:
            for pieza in entidad1.piezas:
                for entidad2 in aux:
                    if pieza in entidad2.piezas and entidad1 != entidad2:
                        entidad1.adyacentes.add(entidad2)

    def conectar_piezas2(self, up, down, upright, upleft, dright, dleft):
        # los argumentos son Tuplas
        creada = False  # variable auxiliar para ver si es nec agregar ciudad
        tiene_ciudad = False
        try:
            conect = self.tablero[up]
            if conect and conect.borde4 == self.pieza_actual.borde1:
                if up in self.jugador_actual.movimientos:
                    # para saber si la pieza se une a otra del mismo jugador
                    self.conectar_piezas(conect, conect.borde4)
                    creada = True
                elif conect.borde4 != "G":
                    self.conectar_piezas(conect, conect.borde4)
                    creada = True
                elif conect.borde4 == "G":
                    if "C" in self.pieza_actual.bordes and not creada:
                        tiene_ciudad = True
        except KeyError:
            self.pieza_actual.grilla = True
        try:
            conect = self.tablero[upright]
            if conect and conect.borde5 == self.pieza_actual.borde2:
                if upright in self.jugador_actual.movimientos:
                    # para saber si la pieza se une a otra del mismo jugador
                    self.conectar_piezas(conect, conect.borde5)
                    creada = True
                elif conect.borde5 != "G":
                    self.conectar_piezas(conect, conect.borde5)
                    creada = True
                elif conect.borde5 == "G":
                    if "C" in self.pieza_actual.bordes and not creada:
                        tiene_ciudad = True

        except KeyError:
            self.pieza_actual.grilla = True
        try:
            conect = self.tablero[dright]
            if conect and conect.borde6 == self.pieza_actual.borde3:
                if dright in self.jugador_actual.movimientos:
                    # para saber si la pieza se une a otra del mismo jugador
                    self.conectar_piezas(conect, conect.borde6)
                    creada = True
                elif conect.borde6 != "G":
                    self.conectar_piezas(conect, conect.borde6)
                    creada = True
                elif conect.borde6 == "G":
                    if "C" in self.pieza_actual.bordes and not creada:
                        tiene_ciudad = True
        except KeyError:
            self.pieza_actual.grilla = True
        try:
            conect = self.tablero[down]
            if conect and conect.borde1 == self.pieza_actual.borde4:
                if down in self.jugador_actual.movimientos:
                    # para saber si la pieza se une a otra del mismo jugador
                    self.conectar_piezas(conect, conect.borde1)
                    creada = True
                elif conect.borde1 != "G":
                    self.conectar_piezas(conect, conect.borde1)
                    creada = True
                elif conect.borde1 == "G":
                    if "C" in self.pieza_actual.bordes and not creada:
                        tiene_ciudad = True
        except KeyError:
            self.pieza_actual.grilla = True
        try:
            conect = self.tablero[dleft]
            if conect and conect.borde2 == self.pieza_actual.borde5:
                if dleft in self.jugador_actual.movimientos:
                    # para saber si la pieza se une a otra del mismo jugador
                    self.conectar_piezas(conect, conect.borde2)
                    creada = True

                elif conect.borde2 != "G":
                    self.conectar_piezas(conect, conect.borde2)
                    creada = True
                elif conect.borde2 == "G":
                    if "C" in self.pieza_actual.bordes and not creada:
                        tiene_ciudad = True
        except KeyError:
            self.pieza_actual.grilla = True
        try:
            conect = self.tablero[upleft]
            if conect and conect.borde3 == self.pieza_actual.borde6:
                if upleft in self.jugador_actual.movimientos:
                    # para saber si la pieza se une a otra del mismo jugador
                    self.conectar_piezas(conect, conect.borde3)
                    creada = True
                elif conect.borde3 != "G":
                    self.conectar_piezas(conect, conect.borde3)
                    creada = True
                elif conect.borde3 == "G":
                    if "C" in self.pieza_actual.bordes and not creada:
                        tiene_ciudad = True
        except KeyError:
            self.pieza_actual.grilla = True
        if tiene_ciudad and not creada:
            self.crear_ciudad(self.pieza_actual)
            if self.pieza_actual.ciudad_separada:
                self.crear_ciudad(self.pieza_actual)
        self.control_ciudades()

    def vecinos(self, i, j):  # determina las posiciones vecinas
        if j % 2 == 0:  # par
            par = True
        else:
            par = False
        up = Tupla(i - 1, j)
        down = Tupla(i + 1, j)
        if par:
            upright = Tupla(i, j + 1)
            upleft = Tupla(i, j - 1)
            dright = Tupla(i + 1, j + 1)
            dleft = Tupla(i + 1, j - 1)
        elif not par:
            upright = Tupla(i - 1, j + 1)
            upleft = Tupla(i - 1, j - 1)
            dright = Tupla(i, j + 1)
            dleft = Tupla(i, j - 1)
        return up, down, upright, upleft, dright, dleft

    def posicion_correcta(self, i, j):
        if j % 2 == 0:  # par
            par = True
        else:
            par = False
        up, down, upright, upleft, dright, dleft = self.vecinos(i, j)
        correcta = False
        try:
            pieza_up = self.tablero[up]
            if pieza_up is not None:
                correcta = True
                if self.pieza_actual.borde1 != pieza_up.borde4:
                    return False
        except KeyError as e:
            pass

        try:
            pieza_down = self.tablero[down]
            if pieza_down is not None:
                correcta = True
                if self.pieza_actual.borde4 != pieza_down.borde1:
                    return False
        except KeyError as e:
            pass

        try:
            pieza_upleft = self.tablero[upleft]
            if pieza_upleft is not None:
                correcta = True
                if self.pieza_actual.borde6 != pieza_upleft.borde3:
                    return False
        except KeyError as e:
            pass

        try:
            pieza_upright = self.tablero[upright]
            if pieza_upright is not None:
                correcta = True
                if self.pieza_actual.borde2 != pieza_upright.borde5:
                    return False
        except KeyError as e:
            pass

        try:
            pieza_dleft = self.tablero[dleft]
            if pieza_dleft is not None:
                correcta = True
                if self.pieza_actual.borde5 != pieza_dleft.borde2:
                    return False
        except KeyError as e:
            pass

        try:
            pieza_dright = self.tablero[dright]
            if pieza_dright is not None:
                correcta = True
                if self.pieza_actual.borde3 != pieza_dright.borde6:
                    return False
        except KeyError as e:
            pass
        if correcta:
            return True
        else:  # cuando no tiene piezas alrededor
            return False

    def cambiar_jugador(self):
        self.contador_erroneas = 0
        if self.jugador_actual == self.jugadores[0]:
            self.jugador_actual = self.jugadores[1]
        else:
            self.jugador_actual = self.jugadores[0]
        return

    def pieza_cerrada(self, pieza, jugador_actual, simulacion):
        i = pieza.posicion[0]
        j = pieza.posicion[1]
        up, down, upright, upleft, dright, dleft = self.vecinos(i, j)
        if not pieza.ciudad_separada:
            self.tablero_objeto.pieza_completada(pieza, jugador_actual,
                                                 simulacion,
                                                 up, down, upright,
                                                 upleft, dright, dleft)
        else:
            pieza.cerrada = True

    def determinar_puntaje(self):
        self.jugadores[0].puntaje = 0
        self.jugadores[1].puntaje = 0
        aux = filter(lambda x: x.tipo == "C", self.entidades)
        cities = ListaLigada()
        for elem in aux:
            cities.append(elem)
        for city in cities:
            for jugador in self.jugadores:
                if city in jugador.entidades:
                    jugador_actual = jugador
            actual_city = Entidad("C")
            for pieza in city.piezas:
                self.pieza_cerrada(pieza, jugador_actual, False)
                if pieza.cerrada and len(city.piezas) > 1:
                    city.completa = True
                else:
                    city.completa = False
                    break
            if city.completa:
                jugador_actual.puntaje += len(city.piezas) * 30
                jugador_actual.puntaje += 40
            else:
                jugador_actual.puntaje += len(city.piezas) * 10

        aux = filter(lambda x: x.tipo == "P" or x.tipo == "R", self.entidades)
        paths = ListaLigada()
        for elem in aux:
            paths.append(elem)
        for path in paths:
            for jugador in self.jugadores:
                if path in jugador.entidades:
                    jugador_actual = jugador
            borde = False
            ciudades = 0
            entidades_contabilizadas = MySet()
            for pieza in path.piezas:
                if pieza.grilla:
                    borde = True
                for adyacente in path.adyacentes:  # adyacente = Entidad
                    if pieza in adyacente.piezas \
                            and adyacente not in entidades_contabilizadas \
                            and adyacente.tipo == "C":
                        ciudades += 1
                        entidades_contabilizadas.add(adyacente)

            if ciudades >= 1 and borde:
                if path.tipo == "P":
                    jugador_actual.puntaje += 20 * ciudades
                    jugador_actual.puntaje += 10 * len(path.piezas) * ciudades
                elif path.tipo == "R":
                    jugador_actual.puntaje += 25 * ciudades
                    jugador_actual.puntaje += 15 * len(path.piezas) * ciudades
            if ciudades == 2:
                if path.tipo == "P":
                    jugador_actual.puntaje += 50
                    jugador_actual.puntaje += 30 * len(path.piezas)
                elif path.tipo == "R":
                    if self.jugador_actual.snitch:
                        return
                    else:
                        ciudades_completas = 0
                        for entidad in entidades_contabilizadas:
                            if entidad.tipo == "C" and entidad.completa:
                                ciudades_completas += 1
                        if ciudades_completas == 1:
                            jugador_actual.puntaje += 55
                            jugador_actual.puntaje += 35 * len(path.piezas)

            if ciudades > 2:
                if path.tipo == "P":
                    jugador_actual.puntaje += 40 * ciudades
                elif path.tipo == "R":
                    if self.jugador_actual.snitch:
                        return
                    else:
                        jugador_actual.puntaje += 45 * ciudades

    def determinar_snitch(self):
        aux = filter(lambda x: x.tipo == "P" or x.tipo == "R", self.entidades)
        paths = ListaLigada()
        for elem in aux:
            paths.append(elem)
        for path in paths:
            for jugador in self.jugadores:
                if path in jugador.entidades:
                    jugador_actual = jugador
            ciudades = 0
            entidades_contabilizadas = MySet()
            for pieza in path.piezas:
                if pieza.grilla:
                    borde = True
                for adyacente in path.adyacentes:  # adyacente = Entidad
                    if pieza in adyacente.piezas \
                            and adyacente not in entidades_contabilizadas \
                            and adyacente.tipo == "C":
                        ciudades += 1
                        entidades_contabilizadas.add(adyacente)
            # determinando si hay snitch dorada
            ciudades_completas = 0
            for ciudad in entidades_contabilizadas:
                for pieza in ciudad.piezas:
                    self.pieza_cerrada(pieza, jugador_actual, False)
                    if pieza.cerrada and len(ciudad.piezas) > 1:
                        ciudad.completa = True
                    else:
                        ciudad.completa = False
                        break
                if ciudad.completa:
                    ciudades_completas += 1
            if ciudades_completas >= 2:
                snitch = True
            else:
                snitch = False
            if ciudades >= 2:
                if path.tipo == "R":
                    if len(path.piezas) >= 3 and snitch:
                        self.jugador_actual.snitch = True  # la tiene
                        return True
        return False

    def determinar_espacios_disponibles(self):
        for pieza in self.tablero.values():
            if pieza is not None:
                return True
        return False

    def colocar_pieza(self, i, j):
        if self.juego_terminado:
            return False
        if self.posicion_correcta(i, j):
            gui.add_piece(i, j)
            if self.tablero[Tupla(i, j)] is None:
                up, down, upright, upleft, dright, dleft = self.vecinos(i, j)
                self.pieza_actual.posicion = Tupla(i, j)
                self.tablero[Tupla(i, j)] = self.pieza_actual
                self.conectar_piezas2(up, down, upright, upleft, dright, dleft)
                self.jugador_actual.movimientos.append(Tupla(i, j))
                self.jugador_actual.piezas.append(self.pieza_actual)
                if self.determinar_snitch():
                    self.terminar_juego()
                self.pieza_actual = self.obtener_pieza_random()
                self.cambiar_jugador()
                if self.mejor_posicion is not None and \
                        isinstance(self.mejor_posicion, Tupla):
                    if self.tablero[self.mejor_posicion] is None:
                        gui.pop_piece(self.mejor_posicion[0],
                                      self.mejor_posicion[1])
                gui.nueva_pieza(self.jugador_actual.color,
                                self.pieza_actual.bordes)
            else:
                pass
        else:
            print("No puedes poner la pieza ahi")
            self.contador_erroneas += 1
            if not self.determinar_espacios_disponibles():
                self.terminar_juego()
            if self.contador_erroneas > 5:
                print("Es posible que no hayan más movimientos posibles. En "
                      "ese caso presiona el botón Terminar Juego para ver al "
                      "ganador.")

    def rotar_pieza(self, orientation):
        if self.juego_terminado:
            return False
        self.pieza_actual.rotar_derecha()

    def retroceder(self):
        if self.juego_terminado:
            return False
        try:
            posicion = self.jugador_actual.movimientos.pop(-1)
            pieza_eliminada = self.tablero[posicion]
            self.jugador_actual.piezas.remove(pieza_eliminada)
            entidades_aux = self.jugador_actual.entidades
            for entidad in entidades_aux:
                if pieza_eliminada in entidad.piezas:
                    if len(entidad.piezas) == 2 and entidad.tipo != "C":
                        self.entidades.remove(entidad)
                        self.jugador_actual.entidades.remove(entidad)
                    elif len(entidad.piezas) >= 2 and entidad.tipo == "C":
                        entidad.piezas.remove(pieza_eliminada)
                    elif len(entidad.piezas) == 1 and entidad.tipo == "C":
                        self.jugador_actual.entidades.remove(entidad)
                        self.entidades.remove(entidad)
                    elif len(entidad.piezas) > 2:
                        entidad.piezas.remove(pieza_eliminada)
            del pieza_eliminada
            self.tablero[posicion] = None
            i = posicion[0]
            j = posicion[1]
            gui.pop_piece(i, j)
            self.cambiar_jugador()
            gui.nueva_pieza(self.jugador_actual.color,
                            self.pieza_actual.bordes)
            return i, j
        except IndexError:
            print(-1, -1)
            return -1, -1

    def terminar_juego(self):
        self.juego_terminado = True
        self.determinar_puntaje()
        gui.set_points(self.jugadores[0].numero, self.jugadores[0].puntaje)
        gui.set_points(self.jugadores[1].numero, self.jugadores[1].puntaje)
        print("Presionaste terminar juego")
        print("Los puntajes son los siguientes:\nJugador 1:",
              self.jugadores[0].puntaje, "\nJugador 2:",
              self.jugadores[1].puntaje)
        if self.jugadores[0].snitch:
            print("Jugador 1 tiene la snitch! Es el ganador")
        elif self.jugadores[1].snitch:
            print("Jugador 2 tiene la snitch! Es el ganador")
        elif self.jugadores[0].puntaje > self.jugadores[1].puntaje:
            print("El ganador es el Jugador 1! Felicidades!!!")
        elif self.jugadores[0].puntaje < self.jugadores[1].puntaje:
            print("El ganador es el Jugador 2! Felicidades!!!")
        else:
            print("Hay un empate!")

    def mejor_jugada(self):
        mejor_puntaje = 0
        mejor_posicion = 0
        for posicion in self.tablero:
            self.guardar_juego()
            i = posicion[0]
            j = posicion[1]
            if self.posicion_correcta(i, j):
                if self.tablero[posicion] is None:
                    up, down, upright, upleft, dright, dleft = self.vecinos(i,
                                                                            j)
                    self.pieza_actual.posicion = posicion
                    self.tablero[posicion] = self.pieza_actual
                    self.conectar_piezas2(up, down, upright, upleft, dright,
                                          dleft)
                    self.jugador_actual.movimientos.append(Tupla(i, j))
                    self.jugador_actual.piezas.append(self.pieza_actual)
                    self.determinar_puntaje()
                    if self.jugador_actual.puntaje > mejor_puntaje:
                        mejor_puntaje = self.jugador_actual.puntaje
                        mejor_posicion = posicion
            self.click_number(self.a)
        return mejor_posicion

    def hint_asked(self):
        if self.juego_terminado:
            return False
        self.mejor_posicion = self.mejor_jugada()
        if isinstance(self.mejor_posicion, Tupla):
            gui.add_hint(self.mejor_posicion[0], self.mejor_posicion[1])
        else:
            print("No hay un hint posible con esa rotacion de pieza o "
                  "no es posible ganar puntaje en esta jugada.")

    def actualizar_tablero(self, nuevo_tablero):
        for posicion, pieza in self.tablero.items():
            if pieza is not None:
                i = posicion[0]
                j = posicion[1]
                gui.pop_piece(i, j)
        for posicion, pieza in nuevo_tablero.elementos.items():
            if pieza is not None:
                if pieza in self.jugadores[0].piezas:
                    jugador = self.jugadores[0]
                else:
                    jugador = self.jugadores[1]
                gui.nueva_pieza(jugador.color, pieza.id)
                i = posicion[0]
                j = posicion[1]
                aux = pieza.id
                while aux != pieza.bordes:
                    gui.rotate_piece()
                    aux = aux[-1] + aux[0:5]
                    self.pieza_actual.rotar_izquierda()
                gui.add_piece(i, j)
        self.tablero_objeto = nuevo_tablero
        self.tablero = nuevo_tablero.elementos
        gui.nueva_pieza(self.jugador_actual.color, self.pieza_actual.id)
        aux = self.pieza_actual.id
        while aux != self.pieza_actual.bordes:
            gui.rotate_piece()
            aux = aux[-1] + aux[0:5]
            self.pieza_actual.rotar_izquierda()

    def click_number(self, number):
        if self.juego_terminado:
            return False
        indice = int(number) - 1
        self.jugadores = self.hist_jugadores[indice]
        self.entidades = self.hist_entidades[indice]
        self.piezas = self.hist_piezas[indice]
        self.cantidad_piezas = Diccionario_Ligado()
        for pieza in self.piezas:
            if pieza.id in self.cantidad_piezas.keys():
                self.cantidad_piezas[pieza.id] += 1
            else:
                self.cantidad_piezas.update(pieza.id, 1)
        self.jugador_actual = self.hist_turno_actual[indice][0]
        self.pieza_actual = self.hist_turno_actual[indice][1]
        self.actualizar_tablero(self.hist_tableros[indice])
        cantidad_historiales = len(self.hist_tableros)
        # borramos todos los historiales siguientes al que elegimos
        for i in range(indice, cantidad_historiales):
            gui.pop_number()
            self.hist_jugadores.pop(indice)
            self.hist_entidades.pop(indice)
            self.hist_piezas.pop(indice)
            self.hist_tableros.pop(indice)
            self.hist_turno_actual.pop(indice)
            # self.a -= 1
        self.a = indice

    def guardar_juego(self):
        if self.juego_terminado:
            return False
        self.a += 1
        gui.add_number(self.a, self.jugador_actual.color)  # next(a)
        tablero_guardado = Tablero()
        jugador1_guardado = Jugador(1, "red")
        jugador2_guardado = Jugador(2, "blue")
        for movimiento in self.jugadores[0].movimientos:
            jugador1_guardado.movimientos.append(movimiento)
        for movimiento in self.jugadores[1].movimientos:
            jugador2_guardado.movimientos.append(movimiento)
        piezas_guardadas = ListaLigada()
        for posicion, pieza in self.tablero.items():
            if pieza is not None:
                pieza_guardada = Pieza(pieza.bordes)
                pieza_guardada.id = pieza.id
                pieza_guardada.posicion = pieza.posicion
                pieza_guardada.ciudad_separada = pieza.ciudad_separada
                pieza_guardada.bifurcacion = pieza.bifurcacion
                pieza_guardada.grilla = pieza.grilla
                for pieza_jug in self.jugadores[0].piezas:
                    if pieza_jug.posicion == posicion:
                        jugador1_guardado.piezas.append(pieza_guardada)
                for pieza_jug in self.jugadores[1].piezas:
                    if pieza_jug.posicion == posicion:
                        jugador2_guardado.piezas.append(pieza_guardada)
                piezas_guardadas.append(pieza_guardada)
            else:
                pieza_guardada = None
            tablero_guardado.elementos[posicion] = pieza_guardada
        self.hist_tableros.append(tablero_guardado)
        pieza_actual = Pieza(self.pieza_actual.id)
        pieza_actual.bordes = self.pieza_actual.bordes
        if self.jugador_actual.numero == 1:
            self.hist_turno_actual.append(Tupla(jugador1_guardado,
                                                pieza_actual))
        elif self.jugador_actual.numero == 2:
            self.hist_turno_actual.append(Tupla(jugador2_guardado,
                                                pieza_actual))
        entidades_guardadas = ListaLigada()
        for entidad in self.entidades:
            entidad_guardada = Entidad(entidad.tipo)
            for pieza_guardada in piezas_guardadas:
                for pieza in entidad.piezas:
                    if pieza.posicion == pieza_guardada.posicion:
                        entidad_guardada.piezas.append(pieza_guardada)
            for jugador in self.jugadores:
                if entidad in jugador.entidades:
                    if jugador.numero == 1:
                        jugador1_guardado.entidades.append(entidad_guardada)
                    elif jugador.numero == 2:
                        jugador2_guardado.entidades.append(entidad_guardada)
            entidades_guardadas.append(entidad_guardada)
        self.hist_entidades.append(entidades_guardadas)

        piezas_guardadas = ListaLigada()
        for pieza in self.piezas:
            new_pieza = Pieza(pieza.bordes)
            piezas_guardadas.append(new_pieza)
        self.hist_piezas.append(piezas_guardadas)
        self.hist_jugadores.append(Tupla(jugador1_guardado, jugador2_guardado))

    def generar_entidad(self, pieza_anterior, pieza_actual, tipo):
        existe = False
        for entidad in self.entidades:
            if entidad.tipo == tipo and pieza_anterior in entidad.piezas:
                if pieza_actual not in entidad.piezas:
                    existe = True
                    if entidad in self.jugador_actual.entidades:
                        entidad.piezas.append(pieza_actual)
                        break
                else:
                    existe = True
        if not existe:
            nueva_entidad = Entidad(tipo)
            nueva_entidad.piezas.append(pieza_anterior)
            nueva_entidad.piezas.append(pieza_actual)
            self.entidades.append(nueva_entidad)
            self.jugador_actual.entidades.append(nueva_entidad)
        aux = ListaLigada()
        for elem in self.jugador_actual.entidades:
            aux.append(elem)
        for entidad1 in self.jugador_actual.entidades:
            for pieza in entidad1.piezas:
                for entidad2 in aux:
                    if pieza in entidad2.piezas and entidad1 != entidad2:
                        entidad1.adyacentes.add(entidad2)

    def generar_entidad2(self, pieza, pieza_conexion_anterior,
                         up, down, upright, upleft, dright, dleft):
        try:
            conect = self.tablero[up]
            if conect and conect.borde4 == pieza.borde1 and \
                    conect != pieza_conexion_anterior:
                if up in self.jugador_actual.movimientos:
                    self.generar_entidad(conect, pieza, conect.borde4)
        except KeyError:
            pass
        try:
            conect = self.tablero[upright]
            if conect and conect.borde5 == pieza.borde2 and \
                    conect != pieza_conexion_anterior:
                if upright in self.jugador_actual.movimientos:
                    self.generar_entidad(conect, pieza, conect.borde5)
        except KeyError:
            pass
        try:
            conect = self.tablero[dright]
            if conect and conect.borde6 == pieza.borde3 and \
                    conect != pieza_conexion_anterior:
                if dright in self.jugador_actual.movimientos:
                    self.generar_entidad(conect, pieza, conect.borde6)
        except KeyError:
            pass
        try:
            conect = self.tablero[down]
            if conect and conect.borde1 == pieza.borde4 and \
                    conect != pieza_conexion_anterior:
                if down in self.jugador_actual.movimientos:
                    self.generar_entidad(conect, pieza, conect.borde1)
        except KeyError:
            pass
        try:
            conect = self.tablero[dleft]
            if conect and conect.borde2 == pieza.borde5 and \
                    conect != pieza_conexion_anterior:
                if dleft in self.jugador_actual.movimientos:
                    self.generar_entidad(conect, pieza, conect.borde2)
        except KeyError:
            pass
        try:
            conect = self.tablero[upleft]
            if conect and conect.borde3 == pieza.borde6 and \
                    conect != pieza_conexion_anterior:
                if upleft in self.jugador_actual.movimientos:
                    self.generar_entidad(conect, pieza, conect.borde3)
        except KeyError:
            pass


if __name__ == '__main__':
    def hook(type, value, traceback):
        print(type)
        print(value)
        print(traceback)


    sys.__excepthook__ = hook

    gui.set_scale(False)  # Any float different from 0
    gui.init()
    gui.set_quality("ultra")  # low, medium, high ultra
    gui.set_animations(False)
    gui.init_grid()
    gui.set_game_interface(MyInterface())  # GUI Listener
    gui.run()
