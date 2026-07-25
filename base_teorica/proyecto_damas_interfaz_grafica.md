# Integración de Interfaz Gráfica al Proyecto de Damas

Este documento toma el proyecto de damas ya construido en POO (clases `Ficha`, `Dama`, `Tablero`, `Jugador`, `Juego`) y le agrega una ventana gráfica. La idea central de todo el documento es una sola: **la interfaz gráfica no reescribe ni una sola regla del juego**. Todo lo que ya se validó y probó (movimiento, captura, captura obligatoria, capturas encadenadas, coronación, victoria) se reutiliza tal cual. La interfaz gráfica solo agrega una forma distinta de mostrar el tablero y de recibir las jugadas: en vez de `print()` e `input()`, dibuja con formas y escucha clics del mouse.

## Qué vamos a usar y por qué

Vamos a usar **Tkinter**, la librería gráfica que viene incluida con Python (no requiere instalar nada con `pip`). Para un juego por turnos como las damas, Tkinter es la opción más eficiente y concisa por tres razones concretas:

- **No hay que instalar nada aparte.** Cualquier Python trae Tkinter incluido, a diferencia de librerías como Pygame, que hay que agregar por separado.
- **No necesita un bucle de refresco constante.** Pygame y otros motores de videojuegos redibujan la pantalla muchas veces por segundo (pensados para animación en tiempo real). En damas nada se mueve solo; el tablero cambia únicamente cuando alguien hace clic. Tkinter funciona por **eventos**: solo ejecuta código cuando pasa algo (un clic), y el resto del tiempo no consume procesamiento de más. Eso es justamente ser eficiente: no gastar recursos dibujando algo que no cambió.
- **Es conciso para este caso de uso.** Con un `Canvas` (una superficie de dibujo) alcanza para pintar un tablero de 8x8 y fichas como círculos, sin necesitar imágenes ni assets externos.

## Qué es un atajo importante en el diseño: separar modelo y vista

Antes del primer paso de código, una decisión de arquitectura: el proyecto va a quedar dividido en dos archivos.

- **`logica_damas.py`**: contiene exactamente las clases `Ficha`, `Dama`, `Tablero`, `Jugador` y `Juego` ya construidas y probadas en la versión anterior, sin cambios. Este archivo no sabe nada de ventanas, ni de dibujo, ni de clics. Es el **modelo**: los datos y las reglas del juego.
- **`interfaz_damas.py`**: es un archivo nuevo, que importa las clases del anterior y agrega todo lo relacionado a mostrar el tablero en una ventana y traducir clics en jugadas. Es la **vista** (lo que se ve) y el **controlador** (lo que traduce la acción del usuario en una llamada al modelo).

Esta separación en dos archivos es la abstracción y el encapsulamiento que ya veníamos usando, pero ahora a nivel de todo el proyecto: `interfaz_damas.py` solo va a llamar métodos públicos de `Juego` y `Tablero` (`jugar_turno`, `obtener_ficha`, `jugador_actual`, etc.), exactamente como antes lo hacía el `input()` de consola. Si mañana se quisiera cambiar Tkinter por otra librería gráfica, `logica_damas.py` no tendría que tocarse ni una línea.

```python
# arriba de interfaz_damas.py
from logica_damas import Ficha, Dama, Tablero, Jugador, Juego
```

`from archivo import Clase1, Clase2` importa esas clases específicas desde otro archivo `.py` que esté en la misma carpeta. Es la misma idea que ya se usa al escribir `from array import array`, pero acá con un archivo propio en vez de uno de la librería estándar.

## Paso 1: El cambio de paradigma — de bucle secuencial a eventos

En la versión de consola, el programa controla el ritmo: `while True:` pide una jugada, espera con `input()`, procesa, y recién ahí vuelve a preguntar. Todo pasa en un orden que el programa decide.

En una interfaz gráfica el control se invierte: el programa arma la ventana, define qué función debe ejecutarse cuando ocurra un clic, y después le entrega el control a Tkinter con `mainloop()`. A partir de ahí, **Tkinter decide cuándo llamar a nuestras funciones**, en respuesta a lo que hace el usuario. A esto se le llama programación dirigida por eventos. Nuestras funciones dejan de ser algo que "se llama a sí mismo en un bucle" y pasan a ser funciones que **otro sistema llama por nosotros** cuando corresponde. Esto es clave para entender por qué el código gráfico se ve distinto al de consola, aunque resuelva el mismo problema.

## Paso 2: Crear la ventana principal

```python
import tkinter as tk

ventana = tk.Tk()
ventana.title("Damas")
ventana.mainloop()
```

- `import tkinter as tk` importa la librería y le da un alias corto (`tk`), para no tener que escribir `tkinter.Tk()` cada vez.
- `tk.Tk()` crea el objeto que representa la ventana principal de la aplicación.
- `ventana.title("Damas")` cambia el texto de la barra de título.
- `ventana.mainloop()` es la línea más importante: le entrega el control del programa a Tkinter, que se queda escuchando eventos (clics, teclas, cerrar ventana) indefinidamente. El código que esté después de esta línea no se ejecuta hasta que la ventana se cierre.

## Paso 3: El `Canvas`, la superficie donde se dibuja el tablero

```python
TAMANIO_CASILLA = 60

lienzo = tk.Canvas(ventana, width=TAMANIO_CASILLA * 8, height=TAMANIO_CASILLA * 8)
lienzo.pack()
```

- `Canvas` es un widget (un elemento visual) pensado específicamente para dibujar formas: rectángulos, óvalos, líneas, texto.
- `TAMANIO_CASILLA = 60` define cuántos píxeles mide cada casilla del tablero. Se usa una constante (una variable que no cambia) para no repetir el número `60` muchas veces sueltas por el código; si más adelante se quiere un tablero más grande o más chico, se cambia en un solo lugar.
- `width=TAMANIO_CASILLA * 8` calcula el ancho total como 8 casillas de ese tamaño — el tablero completo.
- `.pack()` es lo que efectivamente coloca el widget dentro de la ventana. Sin `pack()` (o algún método equivalente), el widget existe en memoria pero no se muestra.

## Paso 4: Convertir entre coordenadas de tablero (fila, columna) y coordenadas de píxeles (x, y)

El `Canvas` no entiende "fila 3, columna 5"; entiende posiciones en píxeles. Necesitamos dos conversiones, una para cada sentido:

```python
def casilla_a_pixeles(fila, columna):
    x0 = columna * TAMANIO_CASILLA
    y0 = fila * TAMANIO_CASILLA
    x1 = x0 + TAMANIO_CASILLA
    y1 = y0 + TAMANIO_CASILLA
    return x0, y0, x1, y1

def pixeles_a_casilla(x, y):
    columna = x // TAMANIO_CASILLA
    fila = y // TAMANIO_CASILLA
    return int(fila), int(columna)
```

- `casilla_a_pixeles` recibe una posición del tablero y devuelve las cuatro coordenadas de píxeles (esquina superior izquierda y esquina inferior derecha) que ocupa esa casilla en la pantalla. Se usa para dibujar.
- `pixeles_a_casilla` hace lo inverso: recibe dónde hizo clic el usuario (en píxeles) y devuelve a qué fila y columna del tablero corresponde. Se usa `//` (división entera) porque interesa saber "en qué casilla cayó el clic", no la posición exacta en píxeles dentro de esa casilla; dividir y descartar el resto es exactamente lo que hace falta para eso.

## Paso 5: Dibujar la grilla del tablero

```python
COLOR_CLARO = "#EEEED2"
COLOR_OSCURO = "#769656"

def dibujar_tablero(lienzo):
    for fila in range(8):
        for columna in range(8):
            x0, y0, x1, y1 = casilla_a_pixeles(fila, columna)
            color = COLOR_OSCURO if (fila + columna) % 2 == 1 else COLOR_CLARO
            lienzo.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
```

Este `for` doble es exactamente el mismo patrón que ya se usó para construir el tablero como matriz en la versión de consola. La diferencia es que acá, en vez de guardar un número en una lista, se dibuja un rectángulo de color en pantalla. La condición `(fila + columna) % 2 == 1` es la misma regla de siempre para decidir casillas oscuras — el mismo concepto, aplicado ahora a dibujo en vez de a datos.

`create_rectangle(x0, y0, x1, y1, fill=color, outline="")` dibuja un rectángulo entre esas dos esquinas, relleno con `color`, sin borde (`outline=""`).

## Paso 6: Dibujar las fichas leyendo el estado real del `Tablero`

Acá es donde se conecta la interfaz con el modelo ya construido:

```python
def dibujar_fichas(lienzo, tablero):
    margen = 8
    for fila in range(8):
        for columna in range(8):
            ficha = tablero.obtener_ficha(fila, columna)
            if ficha is None:
                continue
            x0, y0, x1, y1 = casilla_a_pixeles(fila, columna)
            color_relleno = "white" if ficha.color == "blanco" else "black"
            color_borde = "gold" if isinstance(ficha, Dama) else color_relleno
            lienzo.create_oval(
                x0 + margen, y0 + margen, x1 - margen, y1 - margen,
                fill=color_relleno, outline=color_borde, width=3
            )
```

- `tablero.obtener_ficha(fila, columna)` es el mismo método público que ya existía en `Tablero`. La interfaz nunca toca `tablero._casillas` directamente (el guion bajo sigue significando "no lo toques desde afuera"); solo usa la puerta de entrada oficial que la clase ya ofrecía.
- `isinstance(ficha, Dama)` se usa acá con un propósito puramente visual: dibujar un borde dorado si la ficha es una dama. Es un uso legítimo de `isinstance` distinto del que se usaba en la lógica del juego (ahí se usaba para decidir reglas; acá se usa solo para decidir un color).
- `margen = 8` hace que el círculo sea un poco más chico que la casilla completa, para que se vea prolijo y no toque los bordes.

## Paso 7: Escuchar clics con `bind`

```python
lienzo.bind("<Button-1>", al_hacer_clic)
```

`bind` conecta un evento (`"<Button-1>"`, que en Tkinter significa "clic izquierdo del mouse") con una función (`al_hacer_clic`). A partir de este momento, cada vez que el usuario haga clic izquierdo dentro del `Canvas`, Tkinter va a llamar automáticamente a `al_hacer_clic`, pasándole un objeto `evento` que trae, entre otras cosas, `evento.x` y `evento.y`: la posición exacta del clic en píxeles.

Importante: la función se pasa **sin paréntesis** (`al_hacer_clic`, no `al_hacer_clic()`). Con paréntesis, Python ejecutaría la función inmediatamente y le pasaría a `bind` el resultado de esa ejecución. Sin paréntesis, se le está pasando la función en sí, para que Tkinter la ejecute más adelante, cuando ocurra el clic.

## Paso 8: Traducir un clic en una jugada real

Esta es la función más importante de todo el archivo, porque es el puente entre el mouse del usuario y `Juego.jugar_turno(...)`, que ya conocemos:

```python
origen_seleccionado = None

def al_hacer_clic(evento):
    global origen_seleccionado
    fila, columna = pixeles_a_casilla(evento.x, evento.y)

    if origen_seleccionado is None:
        ficha = juego.tablero.obtener_ficha(fila, columna)
        if ficha is not None and ficha.color == juego.jugador_actual().color:
            origen_seleccionado = (fila, columna)
        return

    origen = origen_seleccionado
    destino = (fila, columna)
    resultado = juego.jugar_turno(origen, destino)
    origen_seleccionado = None

    if resultado != "invalido":
        juego.cambiar_turno()
```

- La idea central: como en pantalla no se puede escribir `input()`, la jugada se arma **con dos clics**. El primer clic elige la ficha de origen (se guarda en `origen_seleccionado`); el segundo clic indica el destino y ahí sí se ejecuta el movimiento.
- Si `origen_seleccionado` todavía es `None`, el clic actual se interpreta como "elegir de dónde mover". Se verifica que en esa casilla haya una ficha y que sea del color del jugador de turno (usando `juego.jugador_actual().color`, el mismo método que ya existía).
- Si `origen_seleccionado` ya tenía un valor, el clic actual se interpreta como el destino. Se arma la jugada y se llama a `juego.jugar_turno(origen, destino)` — exactamente la misma función que en la consola devolvía `"invalido"`, `"cambiar_turno"` o `"continuar_turno"`. La GUI no vuelve a preguntarse "¿esto es diagonal? ¿hay una ficha en el medio?"; todo eso ya lo resuelve el objeto `Juego`.
- Esta versión simplificada ya cambia el turno con cualquier resultado distinto de `"invalido"`. En el paso siguiente se ajusta para manejar bien el caso de las capturas encadenadas.

## Paso 9: Resaltar la selección y mostrar el estado del juego

Sin la consola, hace falta una forma visual de decirle al jugador qué ficha tiene seleccionada, y un lugar para los mensajes que antes eran `print()`:

```python
COLOR_SELECCION = "#F6F669"

def dibujar_tablero_completo(lienzo, juego, origen_seleccionado):
    lienzo.delete("all")
    for fila in range(8):
        for columna in range(8):
            x0, y0, x1, y1 = casilla_a_pixeles(fila, columna)
            color = COLOR_OSCURO if (fila + columna) % 2 == 1 else COLOR_CLARO
            if origen_seleccionado == (fila, columna):
                color = COLOR_SELECCION
            lienzo.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
    dibujar_fichas(lienzo, juego.tablero)
```

- `lienzo.delete("all")` borra todo lo dibujado antes de volver a dibujar. Como el tablero cambia después de cada jugada, hay que "empezar de cero" cada vez que se redibuja; si no se borrara, las fichas viejas quedarían dibujadas debajo de las nuevas.
- La condición `if origen_seleccionado == (fila, columna):` cambia el color de una sola casilla (la seleccionada) antes de dibujarla, dándole feedback visual al jugador sobre qué ficha eligió.

Para los mensajes de estado se usa un `Label` (una etiqueta de texto simple):

```python
etiqueta_estado = tk.Label(ventana, text="", font=("Arial", 14))
etiqueta_estado.pack()

def actualizar_estado(mensaje):
    etiqueta_estado.config(text=mensaje)
```

`config(text=mensaje)` cambia el texto de una etiqueta que ya existe, en vez de crear una etiqueta nueva cada vez. Es el equivalente gráfico de un `print()`: en vez de agregar una línea nueva a la consola, actualiza el mismo cartel en pantalla.

## Paso 10: Encadenar todo — capturas obligatorias, capturas múltiples y fin de partida

Juntando lo anterior, la función de clic final maneja los tres resultados posibles de `jugar_turno` (recordemos: `"invalido"`, `"cambiar_turno"`, `"continuar_turno"`) y también revisa la condición de victoria, reutilizando `hay_ganador()` y `jugador_actual_puede_mover()` tal cual estaban en `Juego`:

```python
def al_hacer_clic(evento):
    global origen_seleccionado
    fila, columna = pixeles_a_casilla(evento.x, evento.y)

    if origen_seleccionado is None:
        ficha = juego.tablero.obtener_ficha(fila, columna)
        if ficha is not None and ficha.color == juego.jugador_actual().color:
            origen_seleccionado = (fila, columna)
            dibujar_tablero_completo(lienzo, juego, origen_seleccionado)
        return

    origen = origen_seleccionado
    destino = (fila, columna)
    resultado = juego.jugar_turno(origen, destino)

    if resultado == "invalido":
        actualizar_estado("Movimiento inválido, intentá de nuevo")
        origen_seleccionado = None
        dibujar_tablero_completo(lienzo, juego, origen_seleccionado)
        return

    if juego.hay_ganador():
        origen_seleccionado = None
        dibujar_tablero_completo(lienzo, juego, origen_seleccionado)
        actualizar_estado(f"¡Gana {juego.jugador_actual().nombre}!")
        return

    if resultado == "continuar_turno":
        origen_seleccionado = destino
        dibujar_tablero_completo(lienzo, juego, origen_seleccionado)
        actualizar_estado("Seguí capturando con la misma ficha")
        return

    origen_seleccionado = None
    juego.cambiar_turno()

    if not juego.jugador_actual_puede_mover():
        dibujar_tablero_completo(lienzo, juego, origen_seleccionado)
        actualizar_estado(f"{juego.jugador_rival().nombre} gana: rival sin movimientos")
        return

    dibujar_tablero_completo(lienzo, juego, origen_seleccionado)
    actualizar_estado(f"Turno de {juego.jugador_actual().nombre} ({juego.jugador_actual().color})")
```

**Puntos clave de esta versión final:**

- Cuando `resultado == "continuar_turno"` (la ficha capturó y puede seguir capturando), `origen_seleccionado` se actualiza a `destino` en vez de volver a `None`. Esto reproduce en la interfaz exactamente lo mismo que hacía `origen_forzado` en la consola: el próximo clic del jugador va a interpretarse directamente como el siguiente destino de captura, sin volver a pedir que elija la ficha (que ya está fija).
- El bloque de `jugador_actual_puede_mover()` se revisa recién después de `cambiar_turno()`, porque la pregunta correcta es "¿el jugador al que ahora le toca jugar tiene movimientos?" — mismo orden que en la versión de consola.
- Ni una sola línea de esta función decide si un movimiento es diagonal, si hay que capturar obligatoriamente, o si una ficha corona. Todo eso sigue viviendo exclusivamente en `logica_damas.py`.

## Programa completo: `interfaz_damas.py`

```python
import tkinter as tk
from logica_damas import Ficha, Dama, Tablero, Jugador, Juego

TAMANIO_CASILLA = 60
COLOR_CLARO = "#EEEED2"
COLOR_OSCURO = "#769656"
COLOR_SELECCION = "#F6F669"


class InterfazDamas:
    def __init__(self, juego):
        self.juego = juego
        self.origen_seleccionado = None

        self.ventana = tk.Tk()
        self.ventana.title("Damas")

        self.lienzo = tk.Canvas(
            self.ventana,
            width=TAMANIO_CASILLA * 8,
            height=TAMANIO_CASILLA * 8
        )
        self.lienzo.pack()
        self.lienzo.bind("<Button-1>", self.al_hacer_clic)

        self.etiqueta_estado = tk.Label(self.ventana, text="", font=("Arial", 14))
        self.etiqueta_estado.pack()

        self.dibujar_tablero()
        self.actualizar_estado()

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

    def dibujar_tablero(self):
        self.lienzo.delete("all")
        for fila in range(8):
            for columna in range(8):
                x0, y0, x1, y1 = self.casilla_a_pixeles(fila, columna)
                color = COLOR_OSCURO if (fila + columna) % 2 == 1 else COLOR_CLARO
                if self.origen_seleccionado == (fila, columna):
                    color = COLOR_SELECCION
                self.lienzo.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

        self.dibujar_fichas()

    def dibujar_fichas(self):
        margen = 8
        for fila in range(8):
            for columna in range(8):
                ficha = self.juego.tablero.obtener_ficha(fila, columna)
                if ficha is None:
                    continue
                x0, y0, x1, y1 = self.casilla_a_pixeles(fila, columna)
                color_relleno = "white" if ficha.color == "blanco" else "black"
                color_borde = "gold" if isinstance(ficha, Dama) else color_relleno
                self.lienzo.create_oval(
                    x0 + margen, y0 + margen, x1 - margen, y1 - margen,
                    fill=color_relleno, outline=color_borde, width=3
                )

    def actualizar_estado(self, mensaje=None):
        if mensaje is None:
            jugador = self.juego.jugador_actual()
            mensaje = f"Turno de {jugador.nombre} ({jugador.color})"
        self.etiqueta_estado.config(text=mensaje)

    def al_hacer_clic(self, evento):
        fila, columna = self.pixeles_a_casilla(evento.x, evento.y)

        if self.origen_seleccionado is None:
            ficha = self.juego.tablero.obtener_ficha(fila, columna)
            if ficha is not None and ficha.color == self.juego.jugador_actual().color:
                self.origen_seleccionado = (fila, columna)
                self.dibujar_tablero()
            return

        origen = self.origen_seleccionado
        destino = (fila, columna)
        resultado = self.juego.jugar_turno(origen, destino)

        if resultado == "invalido":
            self.actualizar_estado("Movimiento inválido, intentá de nuevo")
            self.origen_seleccionado = None
            self.dibujar_tablero()
            return

        if self.juego.hay_ganador():
            self.origen_seleccionado = None
            self.dibujar_tablero()
            ganador = self.juego.jugador_actual().nombre
            self.actualizar_estado(f"¡Gana {ganador}!")
            return

        if resultado == "continuar_turno":
            self.origen_seleccionado = destino
            self.dibujar_tablero()
            self.actualizar_estado("Seguí capturando con la misma ficha")
            return

        self.origen_seleccionado = None
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
```

**Sobre por qué esta versión final está organizada como clase:** los pasos anteriores mostraron las piezas por separado (con variables sueltas y funciones globales) para que se entienda cada una de forma aislada. En el programa completo, todo eso se agrupó dentro de una clase `InterfazDamas`, siguiendo la misma lógica de POO que ya se usó en `logica_damas.py`: `self.origen_seleccionado`, `self.lienzo`, `self.etiqueta_estado` son atributos de instancia, y cada función pasa a ser un método. Esto evita depender de variables globales (`global origen_seleccionado`), que son propensas a errores difíciles de rastrear en programas más grandes.

## Ampliación: efecto hover, arrastrar la ficha y resaltar posiciones válidas

La versión anterior ya es jugable con dos clics (uno para elegir la ficha, otro para el destino). Ahora se agregan tres mejoras de experiencia de usuario, todas dentro de la misma idea: la vista se enriquece, pero **ninguna regla nueva se cocina acá** — todo lo que se muestra sale de preguntarle al objeto `Juego` qué es válido.

- **Hover:** la casilla bajo el cursor se resalta, aunque no se haga clic.
- **Posiciones válidas:** al seleccionar una ficha, se pintan de otro color las casillas donde legalmente puede moverse (reutilizando `movimiento_valido` y `movimiento_captura_valido`, que ya respetan la captura obligatoria).
- **Arrastrar (drag):** la ficha seleccionada puede "levantarse" con el mouse y soltarse en la casilla destino, con un efecto visual de desplazamiento continuo.

### Paso 11: por qué esto necesita más eventos, no más reglas

Hasta ahora solo se escuchaba `<Button-1>` (clic completo). Para hover y arrastre hacen falta eventos más específicos:

| Evento | Cuándo se dispara |
|---|---|
| `<Motion>` | El mouse se mueve dentro del `Canvas`, sin apretar ningún botón |
| `<ButtonPress-1>` | Se **apreta** el botón izquierdo (el instante exacto de bajar el dedo) |
| `<B1-Motion>` | El mouse se mueve **mientras** el botón izquierdo sigue apretado |
| `<ButtonRelease-1>` | Se **suelta** el botón izquierdo |

`<Button-1>` (el que se usaba antes) en realidad es un atajo que combina apretar y soltar en el mismo lugar. Separarlo en estos cuatro eventos es lo que permite distinguir "hizo clic" de "está arrastrando": si entre el `ButtonPress` y el `ButtonRelease` hubo movimientos de `B1-Motion`, hubo arrastre; si no, fue un clic simple. El código va a soportar **ambos estilos** al mismo tiempo: clic-clic (como antes) y presionar-arrastrar-soltar, sin duplicar lógica de juego.

### Paso 12: identificar cada casilla dibujada, para poder repintarla sola

Hasta ahora, cualquier cambio visual implicaba borrar todo el `Canvas` (`delete("all")`) y volver a dibujar las 64 casillas y todas las fichas. Eso es aceptable cuando cambia una jugada completa, pero sería un desperdicio hacerlo en cada mínimo movimiento del mouse durante el hover o el arrastre (que puede disparar decenas de eventos por segundo).

La solución es guardar el identificador que Tkinter le asigna a cada rectángulo al crearlo, para poder pedirle después que cambie *solo su color*, sin tocar el resto:

```python
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
```

- `create_rectangle(...)` en Tkinter **devuelve un número**, un identificador único de ese objeto dibujado. Antes ese valor se descartaba; ahora se guarda en el diccionario `self.ids_casillas`, usando la posición `(fila, columna)` como clave.
- Con ese identificador guardado, más adelante se puede hacer `self.lienzo.itemconfig(id_rect, fill=nuevo_color)`, que le cambia el color a ese rectángulo puntual sin recrear nada. Es la diferencia entre "repintar una sola baldosa" y "levantar el piso entero para cambiar una baldosa".

`_color_de_casilla` centraliza la decisión de qué color le corresponde a cada casilla, combinando las cuatro posibles razones (color base del tablero, destino válido, hover, selección), en orden de prioridad creciente:

```python
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
```

Cada `if` puede pisar el color que dejó el anterior, así que el orden importa: la selección (la más importante de mostrar) se evalúa al final, para que gane por encima del hover o de un destino resaltado si coinciden en la misma casilla.

### Paso 13: el efecto hover, sin redibujar todo el tablero

```python
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
```

- `if casilla == self.casilla_hover: return` es una optimización clave: mientras el mouse se mueve *dentro de la misma casilla*, el evento `<Motion>` se sigue disparando muchas veces, pero no hay nada nuevo que pintar. Cortar acá evita trabajo innecesario.
- Cuando el mouse entra a una casilla distinta, primero se **restaura** el color normal de la casilla anterior (llamando de nuevo a `_color_de_casilla`, que ya sabe si esa casilla era un destino válido o no, por ejemplo) y recién después se pinta la nueva con `COLOR_HOVER`.
- Ninguna línea de esta función llama a `dibujar_tablero()`. Todo el efecto hover se resuelve con dos llamadas puntuales a `itemconfig`, sin tocar el resto de las 63 casillas restantes ni las fichas. Esto es lo que hace que el hover se sienta instantáneo y no consuma recursos de más.

### Paso 14: seleccionar una ficha y calcular sus destinos válidos

```python
def destinos_validos(self, origen):
    fila_o, columna_o = origen
    posibles = Juego.SALTOS_SIMPLES + Juego.SALTOS_CAPTURA
    destinos = []
    for delta_fila, delta_columna in posibles:
        destino = (fila_o + delta_fila, columna_o + delta_columna)
        if self.juego.movimiento_valido(origen, destino) or self.juego.movimiento_captura_valido(origen, destino):
            destinos.append(destino)
    return destinos
```

Esta función prueba las ocho casillas posibles alrededor del origen (las cuatro diagonales simples y las cuatro de captura, reutilizando las mismas listas `SALTOS_SIMPLES` y `SALTOS_CAPTURA` ya definidas como atributos de clase en `Juego`) y se queda solo con las que `Juego` confirma como válidas. Como `movimiento_valido` ya tiene adentro la regla de captura obligatoria, si hay una captura disponible en el tablero, esta función automáticamente va a devolver una lista vacía para los movimientos simples de esa ficha y solo va a marcar las capturas — sin que la interfaz tenga que saber nada sobre esa regla.

### Paso 15: unificar clic y arrastre en un solo flujo

Acá está el corazón de la interacción. Se maneja con tres funciones que se pasan la posta entre sí:

```python
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
```

- `es_ficha_propia`, `sin_seleccion` y `cambiando_de_ficha` son variables booleanas con nombres descriptivos que explican, por sí solas, qué está evaluando cada condición — en vez de un `if` largo y difícil de leer con varias condiciones encadenadas. Es una técnica simple pero muy útil de lógica de programación: nombrar una condición intermedia hace que el código se lea casi como una oración.
- `cambiando_de_ficha` permite un detalle de usabilidad: si ya había una ficha seleccionada, pero el jugador aprieta sobre *otra ficha propia distinta*, la selección cambia a esa nueva ficha en vez de intentar un movimiento inválido hacia ella. La condición `not self.captura_en_curso` es la que impide este cambio de ficha en medio de una cadena de capturas obligatorias (donde hay que seguir con la misma ficha sí o sí).
- Si se cumple `sin_seleccion or cambiando_de_ficha`, se guarda la nueva selección, se calculan y guardan sus destinos válidos, se activa `self.arrastre_activo = True` (avisando "a partir de acá, cualquier arrastre o suelte pertenece a esta selección") y se redibuja.
- Si no, significa que ya había una ficha elegida y este apriete de botón se interpreta directamente como un intento de mover hacia la casilla donde se apretó — esto es lo que sostiene el estilo "clic, clic" de toda la vida, coexistiendo con el arrastre.

```python
def al_arrastrar(self, evento):
    if not self.arrastre_activo or self.id_ficha_arrastrada is None:
        return
    margen = 8
    radio = TAMANIO_CASILLA // 2 - margen
    self.lienzo.coords(
        self.id_ficha_arrastrada,
        evento.x - radio, evento.y - radio, evento.x + radio, evento.y + radio
    )
```

- Esta función se llama en cada `<B1-Motion>`, es decir, muchas veces por segundo mientras se arrastra. Por eso es fundamental que **no redibuje el tablero entero**: solo usa `self.lienzo.coords(id, ...)`, que reposiciona un objeto ya existente (el óvalo de la ficha seleccionada, guardado en `self.id_ficha_arrastrada` al dibujarla) sin borrar ni recrear nada más. Esto es exactamente la misma idea de eficiencia que se usó para el hover, aplicada ahora a un objeto que se mueve.
- El "óvalo que se arrastra" es simplemente la ficha seleccionada, que `dibujar_fichas()` ya dibuja aparte del resto (ver más abajo) para poder moverla libremente sin afectar a las demás.

```python
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
```

- `self.arrastre_activo = False` se ejecuta primero, siempre, apenas se suelta el botón. Esto es importante: evita que un evento de suelte "fantasma" (por ejemplo, el que sigue automáticamente a un clic simple ya resuelto en `al_presionar`) vuelva a disparar un segundo intento de movimiento con la posición vieja del mouse.
- Si el mouse se soltó sobre la misma casilla de origen, no hubo un arrastre real (fue solo un clic para seleccionar): se redibuja para dejar la ficha "en su lugar" y la selección sigue activa, esperando el próximo clic.
- Si se soltó en otra casilla, ahí sí se llama a `intentar_mover`, la misma función central que ya se usaba en la versión anterior sin arrastre.

### Paso 16: dibujar la ficha seleccionada aparte, para poder arrastrarla

```python
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
```

El primer `for` dibuja todas las fichas del tablero **salvo** la que está seleccionada (`continue` la salta). Recién después, si hay una ficha seleccionada, se la dibuja aparte, como último paso — y se guarda su identificador en `self.id_ficha_arrastrada`. Dibujarla al final tiene un motivo visual concreto: en Tkinter, lo último que se dibuja queda "arriba" de lo anterior, así que la ficha seleccionada siempre se ve por encima de cualquier otra al empezar a arrastrarla.

### Paso 17: un ajuste importante — un clic inválido no debe cancelar una captura obligatoria

Al escribir las pruebas de esta versión apareció un bug real: si en medio de una cadena de capturas el jugador hacía clic por error en una casilla que no era un destino válido, `intentar_mover` limpiaba la selección por completo (`origen_seleccionado = None`), como si la obligación de seguir capturando hubiera desaparecido. Eso permitía, después de ese error, elegir cualquier otra ficha — algo que las reglas no permiten en medio de una captura obligatoria.

La corrección es puntual:

```python
if resultado == "invalido":
    if not self.captura_en_curso:
        self.origen_seleccionado = None
        self.destinos_resaltados = []
    self.dibujar_tablero()
    self.actualizar_estado("Movimiento inválido, intentá de nuevo")
    return
```

Si el intento fallido ocurrió mientras `self.captura_en_curso` era `True`, la selección y los destinos resaltados **no se tocan**: la ficha sigue marcada como obligada a continuar, y el jugador puede reintentar sin que el error lo saque del estado en el que debía estar. Este tipo de bug (una condición de error que "limpia de más" y rompe una regla que no tenía nada que ver con ese error puntual) es común cuando se agregan estados nuevos a una función que antes era más simple — por eso conviene siempre revisar, para cada resultado posible, qué parte del estado realmente debería cambiar y cuál no.

## Programa completo: `interfaz_damas.py` (versión con hover, arrastre y destinos válidos)

```python
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
        self.etiqueta_estado.pack()

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
```

## Cómo ejecutarlo

1. Guardar el código de las clases del juego (Ficha, Dama, Tablero, Jugador, Juego, en su versión final sin bugs) en un archivo llamado `logica_damas.py`.
2. Guardar el código de arriba en un archivo llamado `interfaz_damas.py`, en la **misma carpeta**.
3. Ejecutar `python interfaz_damas.py` (o el botón "Run" del editor, apuntando a ese archivo).
4. Se abre una ventana con el tablero. Pasar el mouse resalta la casilla debajo del cursor. Un clic sobre una ficha propia la selecciona (se resalta en amarillo y se marcan en verde sus destinos válidos); desde ahí se puede soltar directamente con otro clic sobre el destino, o arrastrar la ficha con el mouse apretado hasta la casilla deseada y soltarla ahí.

## Por qué esta arquitectura es moderna, eficiente y concisa

- **Moderna**, porque separa claramente el modelo (reglas del juego) de la vista (cómo se muestra), un principio de diseño que se usa en aplicaciones profesionales reales, y porque reemplaza la interacción por texto con una interacción visual directa (clic sobre el tablero, en vez de escribir coordenadas a mano).
- **Eficiente**, porque no hay ningún bucle corriendo todo el tiempo consumiendo procesador: el programa está inactivo hasta que ocurre un evento, y solo redibuja el tablero cuando el estado del juego realmente cambió — no en cada fracción de segundo como haría un motor de videojuego pensado para animación.
- **Concisa**, porque toda la interfaz gráfica se resuelve reutilizando el 100% de la lógica ya construida y probada. No hubo que reescribir `movimiento_valido`, `movimiento_captura_valido`, la captura obligatoria, las capturas encadenadas ni la coronación: la interfaz gráfica es, en esencia, una capa delgada que traduce clics en llamadas a métodos que ya existían.
