"""
interfaz_damas.py

Vista y controlador del juego de damas, usando Tkinter (incluido en Python,
no requiere instalar nada aparte).

Este archivo NO define ninguna regla del juego: solo dibuja el tablero,
escucha el mouse (hover, clic, arrastrar y soltar) y traduce esas acciones
en llamadas a los metodos ya construidos y probados en logica_damas.py
(Juego.jugar_turno, Juego.movimiento_valido, etc.).

Efectos incluidos:
    - Hover: la casilla bajo el cursor se resalta.
    - Destinos validos: al seleccionar una ficha, se marcan sus movimientos
      posibles (respetando la captura obligatoria, ya resuelta en el modelo).
    - Arrastrar y soltar: la ficha seleccionada se puede levantar con el
      mouse y soltar en la casilla destino. Tambien funciona el estilo
      clasico de "clic para elegir, clic para mover".

Para ejecutar: python interfaz_damas.py
(requiere que logica_damas.py este en la misma carpeta)
"""

import tkinter as tk
from logica_damas import Ficha, Dama, Tablero, Jugador, Juego

TAMANIO_CASILLA = 60
COLOR_CLARO = "#EEEED2"
COLOR_OSCURO = "#769656"
COLOR_SELECCION = "#F6F669"
COLOR_DESTINO = "#B7D36B"
COLOR_HOVER = "#D9E28A"


class InterfazDamas:
    def __init__(self, juego):
        self.juego = juego

        self.origen_seleccionado = None
        self.destinos_resaltados = []
        self.casilla_hover = None
        self.arrastre_activo = False
        self.id_ficha_arrastrada = None
        self.captura_en_curso = False
        self.ids_casillas = {}

        self.ventana = tk.Tk()
        self.ventana.title("Damas")
        self.ventana.resizable(False, False)

        self.lienzo = tk.Canvas(
            self.ventana,
            width=TAMANIO_CASILLA * 8,
            height=TAMANIO_CASILLA * 8
        )
        self.lienzo.pack()
        self.lienzo.bind("<Motion>", self.al_mover_mouse)
        self.lienzo.bind("<ButtonPress-1>", self.al_presionar)
        self.lienzo.bind("<B1-Motion>", self.al_arrastrar)
        self.lienzo.bind("<ButtonRelease-1>", self.al_soltar)

        self.etiqueta_estado = tk.Label(self.ventana, text="", font=("Arial", 14))
        self.etiqueta_estado.pack(pady=6)

        self.dibujar_tablero()
        self.actualizar_estado()

    # ---------- conversion de coordenadas ----------

    def casilla_a_pixeles(self, fila, columna):
        x0 = columna * TAMANIO_CASILLA
        y0 = fila * TAMANIO_CASILLA
        x1 = x0 + TAMANIO_CASILLA
        y1 = y0 + TAMANIO_CASILLA
        return x0, y0, x1, y1

    def pixeles_a_casilla(self, x, y):
        columna = x // TAMANIO_CASILLA
        fila = y // TAMANIO_CASILLA
        return int(fila), int(columna)

    # ---------- dibujo ----------

    def _color_de_casilla(self, fila, columna):
        casilla = (fila, columna)
        color = COLOR_OSCURO if (fila + columna) % 2 == 1 else COLOR_CLARO
        if casilla in self.destinos_resaltados:
            color = COLOR_DESTINO
        if self.casilla_hover == casilla:
            color = COLOR_HOVER
        if self.origen_seleccionado == casilla:
            color = COLOR_SELECCION
        return color

    def dibujar_tablero(self):
        self.lienzo.delete("all")
        self.ids_casillas = {}
        for fila in range(8):
            for columna in range(8):
                x0, y0, x1, y1 = self.casilla_a_pixeles(fila, columna)
                color = self._color_de_casilla(fila, columna)
                id_rect = self.lienzo.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
                self.ids_casillas[(fila, columna)] = id_rect
        self.dibujar_fichas()

    def _dibujar_ficha(self, ficha, fila, columna, margen):
        x0, y0, x1, y1 = self.casilla_a_pixeles(fila, columna)
        color_relleno = "white" if ficha.color == "blanco" else "black"
        color_borde = "gold" if isinstance(ficha, Dama) else color_relleno
        return self.lienzo.create_oval(
            x0 + margen, y0 + margen, x1 - margen, y1 - margen,
            fill=color_relleno, outline=color_borde, width=3
        )

    def dibujar_fichas(self):
        margen = 8
        self.id_ficha_arrastrada = None
        for fila in range(8):
            for columna in range(8):
                casilla = (fila, columna)
                if casilla == self.origen_seleccionado:
                    continue
                ficha = self.juego.tablero.obtener_ficha(fila, columna)
                if ficha is None:
                    continue
                self._dibujar_ficha(ficha, fila, columna, margen)

        if self.origen_seleccionado is not None:
            fila, columna = self.origen_seleccionado
            ficha = self.juego.tablero.obtener_ficha(fila, columna)
            self.id_ficha_arrastrada = self._dibujar_ficha(ficha, fila, columna, margen)

    def actualizar_estado(self, mensaje=None):
        if mensaje is None:
            jugador = self.juego.jugador_actual()
            mensaje = f"Turno de {jugador.nombre} ({jugador.color})"
        self.etiqueta_estado.config(text=mensaje)

    # ---------- destinos validos ----------

    def destinos_validos(self, origen):
        fila_o, columna_o = origen
        posibles = Juego.SALTOS_SIMPLES + Juego.SALTOS_CAPTURA
        destinos = []
        for delta_fila, delta_columna in posibles:
            destino = (fila_o + delta_fila, columna_o + delta_columna)
            if self.juego.movimiento_valido(origen, destino) or self.juego.movimiento_captura_valido(origen, destino):
                destinos.append(destino)
        return destinos

    # ---------- hover ----------

    def al_mover_mouse(self, evento):
        fila, columna = self.pixeles_a_casilla(evento.x, evento.y)
        casilla = (fila, columna) if self.juego.tablero.esta_en_rango(fila, columna) else None

        if casilla == self.casilla_hover:
            return

        casilla_anterior = self.casilla_hover
        self.casilla_hover = casilla

        if casilla_anterior is not None and casilla_anterior in self.ids_casillas:
            self.lienzo.itemconfig(
                self.ids_casillas[casilla_anterior],
                fill=self._color_de_casilla(*casilla_anterior)
            )

        if casilla is not None and casilla != self.origen_seleccionado:
            self.lienzo.itemconfig(self.ids_casillas[casilla], fill=COLOR_HOVER)

    # ---------- seleccion, arrastre y jugada ----------

    def al_presionar(self, evento):
        fila, columna = self.pixeles_a_casilla(evento.x, evento.y)
        casilla = (fila, columna)

        en_rango = self.juego.tablero.esta_en_rango(fila, columna)
        ficha_en_casilla = self.juego.tablero.obtener_ficha(fila, columna) if en_rango else None
        es_ficha_propia = (
            ficha_en_casilla is not None
            and ficha_en_casilla.color == self.juego.jugador_actual().color
        )

        sin_seleccion = self.origen_seleccionado is None
        cambiando_de_ficha = (
            not sin_seleccion
            and es_ficha_propia
            and casilla != self.origen_seleccionado
            and not self.captura_en_curso
        )

        if sin_seleccion or cambiando_de_ficha:
            if not es_ficha_propia:
                return
            self.origen_seleccionado = casilla
            self.destinos_resaltados = self.destinos_validos(casilla)
            self.arrastre_activo = True
            self.dibujar_tablero()
            return

        self.arrastre_activo = False
        self.intentar_mover(self.origen_seleccionado, casilla)

    def al_arrastrar(self, evento):
        if not self.arrastre_activo or self.id_ficha_arrastrada is None:
            return
        margen = 8
        radio = TAMANIO_CASILLA // 2 - margen
        self.lienzo.coords(
            self.id_ficha_arrastrada,
            evento.x - radio, evento.y - radio, evento.x + radio, evento.y + radio
        )

    def al_soltar(self, evento):
        if not self.arrastre_activo:
            return
        self.arrastre_activo = False

        fila, columna = self.pixeles_a_casilla(evento.x, evento.y)
        destino = (fila, columna)

        if destino == self.origen_seleccionado:
            self.dibujar_tablero()
            return

        self.intentar_mover(self.origen_seleccionado, destino)

    def intentar_mover(self, origen, destino):
        resultado = self.juego.jugar_turno(origen, destino)

        if resultado == "invalido":
            if not self.captura_en_curso:
                self.origen_seleccionado = None
                self.destinos_resaltados = []
            self.dibujar_tablero()
            self.actualizar_estado("Movimiento inválido, intentá de nuevo")
            return

        if self.juego.hay_ganador():
            self.captura_en_curso = False
            self.origen_seleccionado = None
            self.destinos_resaltados = []
            self.dibujar_tablero()
            self.actualizar_estado(f"¡Gana {self.juego.jugador_actual().nombre}!")
            return

        if resultado == "continuar_turno":
            self.captura_en_curso = True
            self.origen_seleccionado = destino
            self.destinos_resaltados = self.destinos_validos(destino)
            self.dibujar_tablero()
            self.actualizar_estado("Seguí capturando con la misma ficha")
            return

        self.captura_en_curso = False
        self.origen_seleccionado = None
        self.destinos_resaltados = []
        self.juego.cambiar_turno()

        if not self.juego.jugador_actual_puede_mover():
            self.dibujar_tablero()
            ganador = self.juego.jugador_rival().nombre
            self.actualizar_estado(f"{self.juego.jugador_actual().nombre} sin movimientos. ¡Gana {ganador}!")
            return

        self.dibujar_tablero()
        self.actualizar_estado()

    def iniciar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    jugador_blanco = Jugador("Ana", "blanco")
    jugador_negro = Jugador("Luis", "negro")
    juego = Juego(jugador_blanco, jugador_negro)

    interfaz = InterfazDamas(juego)
    interfaz.iniciar()
