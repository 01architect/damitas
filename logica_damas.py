"""
logica_damas.py

Modelo del juego de damas: contiene todas las reglas y el estado del
tablero, sin saber nada de consola ni de interfaz grafica.

Clases:
    Ficha   - una ficha normal, con su color y posicion.
    Dama    - una ficha coronada, hereda de Ficha (se mueve en ambas direcciones).
    Tablero - la matriz 8x8 y las operaciones basicas sobre ella.
    Jugador - nombre y color de cada jugador.
    Juego   - reglas, turnos, captura obligatoria, capturas encadenadas y
              victoria. Incluye tambien un modo de consola (jugar()) que
              se puede usar para probar la logica sin interfaz grafica.
"""


class Ficha:
    def __init__(self, color, fila, columna):
        self.color = color
        self.fila = fila
        self.columna = columna

    def direccion_valida(self, diferencia_fila):
        if self.color == "blanco":
            return diferencia_fila < 0
        return diferencia_fila > 0

    def moverse_a(self, fila, columna):
        self.fila = fila
        self.columna = columna

    def __str__(self):
        return "o" if self.color == "blanco" else "x"


class Dama(Ficha):
    def direccion_valida(self, diferencia_fila):
        return True

    def __str__(self):
        return "O" if self.color == "blanco" else "X"


class Tablero:
    def __init__(self):
        self._casillas = self._crear_casillas_vacias()
        self._colocar_fichas_iniciales()

    def _crear_casillas_vacias(self):
        return [[None for _ in range(8)] for _ in range(8)]

    def _colocar_fichas_iniciales(self):
        for fila in range(8):
            for columna in range(8):
                if (fila + columna) % 2 == 1:
                    if fila < 3:
                        self._casillas[fila][columna] = Ficha("negro", fila, columna)
                    elif fila > 4:
                        self._casillas[fila][columna] = Ficha("blanco", fila, columna)

    def esta_en_rango(self, fila, columna):
        return 0 <= fila < 8 and 0 <= columna < 8

    def esta_vacia(self, fila, columna):
        return self._casillas[fila][columna] is None

    def obtener_ficha(self, fila, columna):
        return self._casillas[fila][columna]

    def colocar_ficha(self, ficha, fila, columna):
        self._casillas[fila][columna] = ficha

    def quitar_ficha(self, fila, columna):
        self._casillas[fila][columna] = None

    def mover_ficha(self, origen, destino):
        fila_o, col_o = origen
        fila_d, col_d = destino
        ficha = self.obtener_ficha(fila_o, col_o)
        self.colocar_ficha(ficha, fila_d, col_d)
        self.quitar_ficha(fila_o, col_o)
        ficha.moverse_a(fila_d, col_d)

    def coronar_si_corresponde(self, ficha):
        if isinstance(ficha, Dama):
            return
        llega_al_final = (
            (ficha.color == "blanco" and ficha.fila == 0) or
            (ficha.color == "negro" and ficha.fila == 7)
        )
        if llega_al_final:
            nueva_dama = Dama(ficha.color, ficha.fila, ficha.columna)
            self.colocar_ficha(nueva_dama, ficha.fila, ficha.columna)

    def contar_fichas(self, color):
        contador = 0
        for fila in range(8):
            for columna in range(8):
                ficha = self._casillas[fila][columna]
                if ficha is not None and ficha.color == color:
                    contador += 1
        return contador

    def imprimir(self):
        print("   " + " ".join(str(c) for c in range(8)))
        for fila in range(8):
            simbolos_fila = []
            for columna in range(8):
                ficha = self._casillas[fila][columna]
                simbolos_fila.append(str(ficha) if ficha is not None else ".")
            print(fila, " ", " ".join(simbolos_fila))


class Jugador:
    def __init__(self, nombre, color):
        self.nombre = nombre
        self.color = color


class Juego:
    SALTOS_SIMPLES = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    SALTOS_CAPTURA = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

    def __init__(self, jugador_blanco, jugador_negro):
        self.tablero = Tablero()
        self.jugadores = [jugador_blanco, jugador_negro]
        self.turno_actual = 0

    def jugador_actual(self):
        return self.jugadores[self.turno_actual]

    def jugador_rival(self):
        return self.jugadores[1 - self.turno_actual]

    def cambiar_turno(self):
        self.turno_actual = 1 - self.turno_actual

    def movimiento_valido(self, origen, destino):
        fila_o, col_o = origen
        fila_d, col_d = destino

        if not self.tablero.esta_en_rango(fila_o, col_o):
            return False
        if not self.tablero.esta_en_rango(fila_d, col_d):
            return False
        if not self.tablero.esta_vacia(fila_d, col_d):
            return False

        ficha = self.tablero.obtener_ficha(fila_o, col_o)
        if ficha is None or ficha.color != self.jugador_actual().color:
            return False

        if self.hay_captura_disponible():
            return False

        diferencia_fila = fila_d - fila_o
        diferencia_col = abs(col_d - col_o)

        if abs(diferencia_fila) != 1 or diferencia_col != 1:
            return False

        return ficha.direccion_valida(diferencia_fila)

    def movimiento_captura_valido(self, origen, destino):
        fila_o, col_o = origen
        fila_d, col_d = destino

        if not self.tablero.esta_en_rango(fila_o, col_o):
            return False
        if not self.tablero.esta_en_rango(fila_d, col_d):
            return False
        if not self.tablero.esta_vacia(fila_d, col_d):
            return False

        ficha = self.tablero.obtener_ficha(fila_o, col_o)
        if ficha is None or ficha.color != self.jugador_actual().color:
            return False

        diferencia_fila = fila_d - fila_o
        diferencia_col = abs(col_d - col_o)

        if abs(diferencia_fila) != 2 or diferencia_col != 2:
            return False

        fila_media = (fila_o + fila_d) // 2
        col_media = (col_o + col_d) // 2
        ficha_intermedia = self.tablero.obtener_ficha(fila_media, col_media)

        return ficha_intermedia is not None and ficha_intermedia.color != ficha.color

    def ejecutar_captura(self, origen, destino):
        fila_o, col_o = origen
        fila_d, col_d = destino
        fila_media = (fila_o + fila_d) // 2
        col_media = (col_o + col_d) // 2

        self.tablero.quitar_ficha(fila_media, col_media)
        self.tablero.mover_ficha(origen, destino)

    def _capturas_desde(self, fila, columna):
        destinos = []
        for delta_fila, delta_columna in self.SALTOS_CAPTURA:
            destino = (fila + delta_fila, columna + delta_columna)
            if self.movimiento_captura_valido((fila, columna), destino):
                destinos.append(destino)
        return destinos

    def _movimientos_simples_desde(self, fila, columna):
        destinos = []
        for delta_fila, delta_columna in self.SALTOS_SIMPLES:
            destino = (fila + delta_fila, columna + delta_columna)
            if self.movimiento_valido((fila, columna), destino):
                destinos.append(destino)
        return destinos

    def hay_captura_disponible(self):
        color = self.jugador_actual().color
        for fila in range(8):
            for columna in range(8):
                ficha = self.tablero.obtener_ficha(fila, columna)
                if ficha is not None and ficha.color == color:
                    if self._capturas_desde(fila, columna):
                        return True
        return False

    def jugador_actual_puede_mover(self):
        color = self.jugador_actual().color
        for fila in range(8):
            for columna in range(8):
                ficha = self.tablero.obtener_ficha(fila, columna)
                if ficha is not None and ficha.color == color:
                    if self._capturas_desde(fila, columna):
                        return True
                    if self._movimientos_simples_desde(fila, columna):
                        return True
        return False

    def jugar_turno(self, origen, destino):
        if self.movimiento_captura_valido(origen, destino):
            self.ejecutar_captura(origen, destino)
            ficha_movida = self.tablero.obtener_ficha(*destino)
            self.tablero.coronar_si_corresponde(ficha_movida)
            if self._capturas_desde(*destino):
                return "continuar_turno"
            return "cambiar_turno"

        if self.movimiento_valido(origen, destino):
            self.tablero.mover_ficha(origen, destino)
            ficha_movida = self.tablero.obtener_ficha(*destino)
            self.tablero.coronar_si_corresponde(ficha_movida)
            return "cambiar_turno"

        return "invalido"

    def hay_ganador(self):
        return self.tablero.contar_fichas(self.jugador_rival().color) == 0

    def _pedir_posicion(self, mensaje):
        entrada = input(mensaje)
        partes = entrada.split()
        if len(partes) != 2:
            print("Ingresá dos números separados por un espacio, por ejemplo: 5 0")
            return None
        try:
            fila = int(partes[0])
            columna = int(partes[1])
        except ValueError:
            print("Los valores ingresados deben ser números enteros.")
            return None
        return (fila, columna)

    def jugar(self):
        """Modo de consola: util para probar la logica sin interfaz grafica."""
        origen_forzado = None

        while True:
            self.tablero.imprimir()

            if not self.jugador_actual_puede_mover():
                print(f"{self.jugador_actual().nombre} no tiene movimientos posibles. "
                      f"¡Gana {self.jugador_rival().nombre}!")
                break

            print(f"Turno de {self.jugador_actual().nombre} ({self.jugador_actual().color})")

            if origen_forzado is not None:
                origen = origen_forzado
                print(f"Debés continuar capturando con la ficha en {origen}")
            else:
                origen = self._pedir_posicion("Fila y columna de origen (ej: 5 0): ")
                if origen is None:
                    continue

            destino = self._pedir_posicion("Fila y columna de destino (ej: 4 1): ")
            if destino is None:
                continue

            resultado = self.jugar_turno(origen, destino)

            if resultado == "invalido":
                print("Movimiento inválido, intenta de nuevo.")
                continue

            if self.hay_ganador():
                self.tablero.imprimir()
                print(f"¡Gana {self.jugador_actual().nombre}!")
                break

            if resultado == "continuar_turno":
                origen_forzado = destino
                continue

            origen_forzado = None
            self.cambiar_turno()


if __name__ == "__main__":
    # Ejecutar este archivo directamente arranca la version de CONSOLA,
    # util para probar la logica sin la interfaz grafica.
    # Para la version con ventana, ejecutar interfaz_damas.py
    jugador_blanco = Jugador("Ana", "blanco")
    jugador_negro = Jugador("Luis", "negro")
    juego = Juego(jugador_blanco, jugador_negro)
    juego.jugar()
