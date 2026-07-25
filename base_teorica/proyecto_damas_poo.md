# Proyecto de Damas con Programación Orientada a Objetos (POO)

Este documento continúa el proyecto de damas, pero reconstruye la lógica desde cero usando clases y objetos. La idea no es "traducir" el código anterior línea por línea, sino rediseñar el problema con otra forma de pensar: en vez de tener un arreglo suelto y funciones que lo reciben como parámetro una y otra vez, vamos a tener objetos que saben manejar sus propios datos.

## Por qué dar el salto desde la versión con funciones

En la versión anterior, casi todas las funciones necesitaban recibir `tablero` y muchas también `turno`:

```python
mover(tablero, origen, destino)
movimiento_valido(tablero, origen, destino, turno)
contar_fichas(tablero, turno)
```

Esto funciona, pero tiene dos problemas que se agravan a medida que el proyecto crece:

- **El dato viaja por todos lados.** `tablero` es un parámetro casi obligatorio en cada función, aunque conceptualmente todas esas funciones "son cosas que le pasan al tablero".
- **El significado vive fuera del dato.** Un `1`, un `2`, un `3` o un `4` en el arreglo no dicen nada por sí solos; hay que recordar la convención ("3 es una dama del jugador 1") en cada lugar del código donde se usa.

La Programación Orientada a Objetos ataca exactamente estos dos problemas.

## Qué es la Programación Orientada a Objetos

POO es una forma de organizar el código agrupando **datos** (llamados atributos) y las **funciones que operan sobre esos datos** (llamadas métodos) dentro de una misma unidad, llamada **clase**.

Dos conceptos hay que separar bien desde el principio:

- **Clase:** es el molde, la definición. Describe qué atributos y qué métodos va a tener cualquier cosa creada a partir de ella. Es como el plano de una casa: no es una casa, es la descripción de cómo construirla.
- **Objeto (o instancia):** es una cosa concreta construida a partir de ese molde. Si `Ficha` es la clase, cada ficha individual del tablero (con su propia fila, columna y color) es un objeto de esa clase. Del mismo plano de casa se pueden construir muchas casas distintas, cada una en su propia dirección.

En la versión anterior, el "molde" de una ficha no existía como tal: era simplemente un número dentro de una matriz. En esta versión, cada ficha va a ser un objeto real, con su propio estado.

## Los cuatro pilares de la POO, aplicados a este proyecto

Antes de programar, conviene tener claro qué vamos a estar demostrando en cada clase:

**1. Encapsulamiento.** Es guardar los datos internos de un objeto junto con las operaciones que los manipulan, y no dejar que el resto del programa los toque directamente. La clase `Tablero` va a guardar la matriz internamente (`self._casillas`) y el resto del programa nunca va a escribir directamente sobre esa matriz: solo va a poder pedirle al tablero que haga cosas (`tablero.mover_ficha(...)`).

**2. Abstracción.** Es exponer una interfaz simple hacia afuera, ocultando los detalles de cómo está resuelto por dentro. La clase `Juego` va a llamar `tablero.mover_ficha(origen, destino)` sin saber (ni necesitar saber) que por dentro hay una lista de listas. Si mañana cambiamos la representación interna del tablero, `Juego` no se entera.

**3. Herencia.** Es crear una clase nueva a partir de otra ya existente, reutilizando lo que ya tiene y agregando o modificando solo lo que cambia. Una dama sigue siendo una ficha (tiene color, tiene posición), pero se mueve distinto. En vez de repetir todo, la clase `Dama` va a heredar de `Ficha`.

**4. Polimorfismo.** Es que distintos objetos respondan de manera distinta al mismo mensaje (al mismo método llamado), sin que quien llama tenga que saber con cuál está tratando. `Juego` va a llamar `ficha.direccion_valida(diferencia_fila)` tanto para una ficha normal como para una dama, y cada una va a decidir la respuesta a su manera, con su propia versión del método.

## Diseño de clases

Antes de escribir código, definimos qué clase es responsable de qué:

- **`Ficha`**: sabe su color y su posición, y sabe decidir si una dirección de movimiento es válida para ella.
- **`Dama`**: es una `Ficha` que se mueve en ambas direcciones (hereda de `Ficha`).
- **`Tablero`**: sabe qué hay en cada casilla, sabe colocar y quitar fichas, sabe imprimirse y sabe contar fichas por color. No sabe nada de reglas del juego ni de turnos.
- **`Jugador`**: representa a una persona jugando, con su nombre y su color.
- **`Juego`**: conoce las reglas (qué movimiento es válido, cuándo hay captura, cuándo se gana) y coordina el turno entre los dos jugadores, usando al `Tablero` como herramienta.

Esta separación de responsabilidades es en sí misma una decisión de diseño orientado a objetos: cada clase hace una sola cosa y la hace bien, en vez de tener una única función gigante que hace todo.

## Paso 1: Clase `Ficha`

```python
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
```

**Explicación sintaxis por sintaxis:**

- `class Ficha:` declara una clase nueva llamada `Ficha`. Todo lo indentado debajo pertenece a esa clase.
- `def __init__(self, color, fila, columna):` es el **constructor**. Es un método especial que Python ejecuta automáticamente cada vez que se crea un objeto nuevo con `Ficha(...)`. Su trabajo es dejar el objeto listo, con sus atributos iniciales cargados.
- `self` es el primer parámetro de **todos** los métodos de una clase, y representa "este objeto en particular, el que está ejecutando el método ahora mismo". No se pasa explícitamente al llamar al método (Python lo pasa solo); solo se declara en la definición.
- `self.color = color` crea un **atributo de instancia**: un dato que le pertenece únicamente a ese objeto. Cada `Ficha` que se cree va a tener su propio `color`, su propia `fila` y su propia `columna`, independientes entre sí. Esto es exactamente lo que antes eran cuatro números sueltos (1, 2, 3, 4) codificados en el arreglo: ahora es un objeto con estado propio.
- `direccion_valida(self, diferencia_fila)` es un **método**: una función definida dentro de la clase que puede leer y usar los atributos del objeto (`self.color`) para decidir algo. Devuelve `True` o `False` según si esa ficha, con su color, puede moverse en esa dirección.
- `moverse_a(self, fila, columna)` actualiza la posición del objeto. Nótese que la ficha misma es responsable de actualizar su propia posición; nadie de afuera le va a "pisar" `fila` y `columna` directamente.
- `def __str__(self):` es un **método especial** (reconocible porque su nombre empieza y termina con doble guion bajo, por eso se los llama "dunder methods", de *double underscore*). Python lo llama automáticamente cuando alguien hace `str(objeto)` o `print(objeto)`. Acá lo vamos a usar explícitamente al imprimir el tablero para decidir qué símbolo mostrar.

**Cómo se crea un objeto a partir de esta clase:**

```python
ficha_ejemplo = Ficha("blanco", 5, 0)
print(ficha_ejemplo.color)      # blanco
print(ficha_ejemplo.fila)       # 5
print(str(ficha_ejemplo))       # o
```

`Ficha("blanco", 5, 0)` llama automáticamente a `__init__`, pasando `"blanco"` a `color`, `5` a `fila` y `0` a `columna` (el `self` lo completa Python solo). El resultado, `ficha_ejemplo`, es un objeto con esos tres atributos ya cargados.

## Paso 2: Clase `Dama` — Herencia y Polimorfismo en acción

```python
class Dama(Ficha):
    def direccion_valida(self, diferencia_fila):
        return True

    def __str__(self):
        return "O" if self.color == "blanco" else "X"
```

**Explicación sintaxis por sintaxis:**

- `class Dama(Ficha):` es la sintaxis de **herencia**: el nombre entre paréntesis es la clase de la que se hereda. Esto significa que `Dama` automáticamente tiene todo lo que tiene `Ficha`: el constructor `__init__`, el atributo `color`, `fila`, `columna`, y el método `moverse_a`, sin que se haya vuelto a escribir una sola línea de eso. `Dama` no necesitó redefinir `__init__` porque le sirve exactamente el mismo que ya tiene `Ficha`.
- Lo único que `Dama` **sobrescribe** (redefine) es `direccion_valida` y `__str__`. A esto se le llama **method overriding**: la subclase define su propia versión de un método que ya existía en la clase base, y esa nueva versión es la que se usa cuando el objeto es de tipo `Dama`.
- Esto es **polimorfismo** en estado puro: en el resto del programa vamos a escribir `ficha.direccion_valida(diferencia_fila)`, sin preguntar nunca "¿sos una Ficha normal o una Dama?". Python resuelve solo, en tiempo de ejecución, cuál de las dos versiones del método ejecutar, según el tipo real del objeto que está en `ficha`. El código que llama al método no necesita ni un `if` para distinguir los casos.
- `Dama` **es una** `Ficha` (relación *"is-a"*, propia de la herencia): en cualquier lugar del código donde se espera una `Ficha`, también sirve una `Dama`, porque una `Dama` tiene todo lo que una `Ficha` tiene, y más.

## Paso 3: Clase `Tablero` — Encapsulamiento y Abstracción

```python
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
```

**Explicación sintaxis por sintaxis:**

- `self._casillas` guarda la matriz 8x8. El guion bajo inicial (`_casillas`) es una **convención** de Python para decir "esto es un detalle interno de la clase, no lo uses directamente desde afuera". Python no lo bloquea técnicamente (no existe un `private` real como en Java), pero cualquier programador que lea `_casillas` entiende que no debería tocarlo desde fuera de la clase. Esto es el encapsulamiento: los datos internos quedan "escondidos" detrás de métodos públicos.
- `self._crear_casillas_vacias()` y `self._colocar_fichas_iniciales()` también llevan guion bajo porque son **métodos auxiliares internos**: existen solo para que `__init__` pueda organizarse en pasos más chicos y legibles, pero no están pensados para que se llamen desde afuera de la clase.
- `[[None for _ in range(8)] for _ in range(8)]` es una lista por comprensión anidada: arma una matriz de 8x8 donde cada casilla vale `None` (nada). Es equivalente a dos `for` anidados que van haciendo `.append()`, como en la versión anterior, pero en una sola línea. El guion bajo `_` como nombre de variable es una convención para decir "esta variable no me importa, no la voy a usar dentro del ciclo".
- `obtener_ficha`, `colocar_ficha`, `quitar_ficha`, `esta_vacia`, `esta_en_rango` son la **interfaz pública** del tablero: un conjunto reducido y claro de operaciones que cualquier otra parte del programa puede usar para interactuar con el tablero, sin necesitar saber que por dentro hay una lista de listas. Esto es la abstracción: `Juego` va a usar estos métodos sin preocuparse de cómo están implementados.
- `mover_ficha` reutiliza `obtener_ficha`, `colocar_ficha` y `quitar_ficha` en vez de acceder directamente a `self._casillas[...]`. Aunque técnicamente podría, dentro de la misma clase también conviene usar los propios métodos: si mañana cambia la representación interna, solo hay que ajustar esos métodos base una vez.
- `ficha.moverse_a(fila_d, col_d)`, al final de `mover_ficha`, es clave: el tablero mueve la ficha de lugar en la matriz, pero es la propia ficha la que actualiza sus atributos `fila` y `columna`. Cada objeto es responsable de su propio estado.
- `isinstance(ficha, Dama)` es una función incorporada de Python que pregunta "¿este objeto es de la clase `Dama` (o de una que herede de ella)?". Se usa para no volver a coronar una ficha que ya es dama.
- `Dama(ficha.color, ficha.fila, ficha.columna)` crea un objeto **nuevo** de tipo `Dama`, reemplazando a la ficha original en esa casilla. Fíjense que esto funciona porque `Dama` heredó el mismo constructor `__init__` de `Ficha`, así que se construye exactamente igual, solo que el objeto resultante es de otra clase (y por lo tanto usa la versión de `direccion_valida` y `__str__` de `Dama`).
- `str(ficha) if ficha is not None else "."` en `imprimir` es donde se ve el polimorfismo funcionando: no le importa si `ficha` es una `Ficha` o una `Dama`, simplemente llama `str(ficha)` y cada objeto responde con su propio símbolo (`"o"`/`"x"` o `"O"`/`"X"`) gracias a que cada clase definió su propio `__str__`.

## Paso 4: Clase `Jugador`

```python
class Jugador:
    def __init__(self, nombre, color):
        self.nombre = nombre
        self.color = color
```

**Explicación:** es la clase más simple del proyecto, y está bien que sea así. Su única responsabilidad es representar a una persona jugando, con nombre y color. No sabe nada de reglas ni de tablero — esa separación de responsabilidades es intencional: cada clase debe encargarse de una sola cosa.

## Paso 5: Clase `Juego` — el orquestador

```python
class Juego:
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

        if not self.tablero.esta_en_rango(fila_d, col_d):
            return False
        if not self.tablero.esta_vacia(fila_d, col_d):
            return False

        ficha = self.tablero.obtener_ficha(fila_o, col_o)
        if ficha is None or ficha.color != self.jugador_actual().color:
            return False

        diferencia_fila = fila_d - fila_o
        diferencia_col = abs(col_d - col_o)

        if abs(diferencia_fila) != 1 or diferencia_col != 1:
            return False

        return ficha.direccion_valida(diferencia_fila)

    def movimiento_captura_valido(self, origen, destino):
        fila_o, col_o = origen
        fila_d, col_d = destino

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

    def jugar_turno(self, origen, destino):
        if self.movimiento_captura_valido(origen, destino):
            self.ejecutar_captura(origen, destino)
        elif self.movimiento_valido(origen, destino):
            self.tablero.mover_ficha(origen, destino)
        else:
            return False

        ficha_movida = self.tablero.obtener_ficha(*destino)
        self.tablero.coronar_si_corresponde(ficha_movida)
        return True

    def hay_ganador(self):
        return self.tablero.contar_fichas(self.jugador_rival().color) == 0

    def jugar(self):
        while True:
            self.tablero.imprimir()
            print(f"Turno de {self.jugador_actual().nombre} ({self.jugador_actual().color})")

            entrada_origen = input("Fila y columna de origen (ej: 5 0): ")
            entrada_destino = input("Fila y columna de destino (ej: 4 1): ")

            fila_o, col_o = map(int, entrada_origen.split())
            fila_d, col_d = map(int, entrada_destino.split())
            origen = (fila_o, col_o)
            destino = (fila_d, col_d)

            if not self.jugar_turno(origen, destino):
                print("Movimiento inválido, intenta de nuevo.")
                continue

            if self.hay_ganador():
                self.tablero.imprimir()
                print(f"¡Gana {self.jugador_actual().nombre}!")
                break

            self.cambiar_turno()
```

**Explicación sintaxis por sintaxis:**

- `__init__` recibe dos objetos `Jugador` ya construidos (no sus datos sueltos) y arma sus propios atributos: `self.tablero` (composición: `Juego` **tiene un** `Tablero`, no **es un** `Tablero`), `self.jugadores` (una lista con los dos jugadores) y `self.turno_actual` (un índice, 0 o 1, que indica a quién le toca).
- Nótese la diferencia con la herencia de `Dama`/`Ficha`: ahí la relación era *"is-a"* (una Dama **es** una Ficha). Acá la relación es *"has-a"* (un Juego **tiene** un Tablero, **tiene** jugadores). A esto se lo llama **composición**, y es tan importante como la herencia en el diseño orientado a objetos: no todo se resuelve heredando, muchas veces la relación correcta es "este objeto usa a otro objeto como parte de su propio estado".
- `jugador_actual()` y `jugador_rival()` devuelven objetos `Jugador` completos (no solo el color), así el resto del código puede preguntar `self.jugador_actual().color` o `self.jugador_actual().nombre` según lo que necesite en cada momento.
- `self.turno_actual = 1 - self.turno_actual` es el mismo truco aritmético que antes usábamos con el operador ternario, adaptado a un índice de lista: si `turno_actual` es 0, `1 - 0` da 1; si es 1, `1 - 0`... da 1, y `1 - 1` da 0. Alterna entre las dos posiciones de la lista `self.jugadores`.
- `movimiento_valido` y `movimiento_captura_valido` tienen prácticamente la misma lógica que en la versión con funciones, pero ahora **no reciben `tablero` como parámetro**: lo toman de `self.tablero`, porque `Juego` ya lo tiene guardado como atributo propio desde que se creó. Ese es justamente el problema que resolvimos: el dato ya no viaja de función en función, vive donde corresponde.
- `ficha.direccion_valida(diferencia_fila)` es la línea donde se usa el polimorfismo explicado antes: `Juego` no pregunta si `ficha` es Dama o no, simplemente delega la decisión al objeto.
- `jugar_turno` centraliza la decisión de "¿qué tipo de jugada es esta?" y después llama a `self.tablero.coronar_si_corresponde(...)`, delegando en el tablero la responsabilidad de decidir si corresponde coronar. `Juego` no sabe (ni le importa) cómo se corona una ficha por dentro; solo sabe que puede pedírselo al tablero.
- `self.tablero.obtener_ficha(*destino)`: el asterisco antes de `destino` es **desempaquetado de argumentos**. Como `destino` es una tupla `(fila, columna)`, escribir `obtener_ficha(*destino)` es equivalente a escribir `obtener_ficha(destino[0], destino[1])`, pero más corto.
- `jugar()` es el bucle principal, prácticamente igual en estructura al de la versión anterior (`while True`, `input`, `continue`, `break`), pero ahora todas las llamadas son a métodos de `self` (`self.jugador_actual()`, `self.jugar_turno(...)`, `self.hay_ganador()`) en vez de a funciones sueltas con `tablero` y `turno` como parámetros.

## Programa completo

```python
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

        if not self.tablero.esta_en_rango(fila_d, col_d):
            return False
        if not self.tablero.esta_vacia(fila_d, col_d):
            return False

        ficha = self.tablero.obtener_ficha(fila_o, col_o)
        if ficha is None or ficha.color != self.jugador_actual().color:
            return False

        diferencia_fila = fila_d - fila_o
        diferencia_col = abs(col_d - col_o)

        if abs(diferencia_fila) != 1 or diferencia_col != 1:
            return False

        return ficha.direccion_valida(diferencia_fila)

    def movimiento_captura_valido(self, origen, destino):
        fila_o, col_o = origen
        fila_d, col_d = destino

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

    def jugar_turno(self, origen, destino):
        if self.movimiento_captura_valido(origen, destino):
            self.ejecutar_captura(origen, destino)
        elif self.movimiento_valido(origen, destino):
            self.tablero.mover_ficha(origen, destino)
        else:
            return False

        ficha_movida = self.tablero.obtener_ficha(*destino)
        self.tablero.coronar_si_corresponde(ficha_movida)
        return True

    def hay_ganador(self):
        return self.tablero.contar_fichas(self.jugador_rival().color) == 0

    def jugar(self):
        while True:
            self.tablero.imprimir()
            print(f"Turno de {self.jugador_actual().nombre} ({self.jugador_actual().color})")

            entrada_origen = input("Fila y columna de origen (ej: 5 0): ")
            entrada_destino = input("Fila y columna de destino (ej: 4 1): ")

            fila_o, col_o = map(int, entrada_origen.split())
            fila_d, col_d = map(int, entrada_destino.split())
            origen = (fila_o, col_o)
            destino = (fila_d, col_d)

            if not self.jugar_turno(origen, destino):
                print("Movimiento inválido, intenta de nuevo.")
                continue

            if self.hay_ganador():
                self.tablero.imprimir()
                print(f"¡Gana {self.jugador_actual().nombre}!")
                break

            self.cambiar_turno()


if __name__ == "__main__":
    jugador_blanco = Jugador("Ana", "blanco")
    jugador_negro = Jugador("Luis", "negro")
    juego = Juego(jugador_blanco, jugador_negro)
    juego.jugar()
```

**Sobre la última parte del archivo:**

```python
if __name__ == "__main__":
    ...
```

`__name__` es una variable especial que Python le asigna automáticamente a cada archivo. Cuando el archivo se ejecuta directamente (por ejemplo `python damas.py`), `__name__` vale `"__main__"`. Pero si este archivo se importa desde otro (`import damas`), `__name__` va a valer `"damas"`, no `"__main__"`. Este `if` es una convención estándar de Python: asegura que el juego solo arranque cuando se ejecuta el archivo directamente, y no si en el futuro alguien quiere reutilizar las clases `Ficha`, `Tablero`, etc. desde otro archivo sin que se dispare una partida automáticamente.

## Comparación directa: antes (funciones) y después (POO)

| Aspecto | Con funciones sueltas | Con clases y objetos |
|---|---|---|
| Representar una ficha | Un número (1, 2, 3, 4) dentro del arreglo | Un objeto `Ficha` o `Dama` con atributos propios |
| Pasar el tablero | Parámetro `tablero` en casi todas las funciones | Atributo `self.tablero`, ya disponible dentro de `Juego` |
| Distinguir ficha normal de dama | `if ficha in (1, 3)` repetido en varios lugares | Cada clase resuelve su propio comportamiento (polimorfismo) |
| Agregar una nueva regla de movimiento para damas | Modificar varios `if` dispersos por el código | Modificar un solo método (`direccion_valida`) en `Dama` |
| Ocultar detalles internos del tablero | No hay forma de ocultarlos, todo el código accede al arreglo | `_casillas` queda encapsulado detrás de métodos públicos |

## Versión robusta: bugs corregidos y reglas completas

La versión anterior ya funciona, pero tiene bugs reales (no solo reglas simplificadas a propósito) y le faltan reglas que cualquier jugador de damas esperaría. Acá se corrige todo, explicando cada problema antes de mostrar la solución.

### Bug 1: los índices negativos no dan error, "dan la vuelta"

En `movimiento_valido` y `movimiento_captura_valido`, el código validaba que la casilla **destino** estuviera dentro del tablero (`esta_en_rango`), pero nunca validaba la casilla **origen** antes de usarla para indexar la matriz con `self._casillas[fila][columna]`.

Esto no tira error en Python, y ahí está el problema: en una lista, el índice `-1` no es inválido, es **el último elemento**. Si un jugador escribe como origen `-1 0`, Python no explota: silenciosamente devuelve `self._casillas[-1][0]`, que es la fila 7 (la última). El programa terminaría dejando mover una ficha que el jugador nunca eligió realmente, sin ningún aviso de error. Es un bug silencioso, de los más peligrosos porque no se nota hasta que ya generó un resultado incorrecto.

**Corrección:** agregar la validación de rango también sobre el origen, antes de leer nada de esa posición:

```python
if not self.tablero.esta_en_rango(fila_o, col_o):
    return False
```

### Bug 2: una entrada de teclado mal escrita rompe todo el programa

En el bucle `jugar()`, la línea `fila_o, col_o = map(int, entrada_origen.split())` asume que el jugador siempre escribe exactamente dos números separados por un espacio. Si escribe una letra, un solo número, o tres números, Python lanza una excepción (`ValueError`) que no está capturada en ningún lado, y el programa entero se cae con un traceback en lugar de simplemente pedir la jugada de nuevo.

**Corrección:** se agrega un método dedicado a pedir una posición, que valida la cantidad de valores y controla el error de conversión con `try/except`:

```python
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
```

`try/except` es la forma de Python de decir "intentá ejecutar esto; si falla de esta manera puntual (`ValueError`), no dejes que rompa el programa, ejecutá esta otra cosa en su lugar". Si `_pedir_posicion` devuelve `None`, el bucle principal vuelve a pedir la jugada con `continue`, en vez de cortarse.

### Regla faltante 1: captura obligatoria

En damas, si un jugador tiene al menos una captura disponible con cualquiera de sus fichas, **está obligado a capturar**: no puede hacer un movimiento simple mientras haya una captura posible. La versión anterior no exigía esto.

**Implementación:** un método que recorre todo el tablero buscando si el jugador de turno tiene alguna captura disponible, y se usa dentro de `movimiento_valido` para bloquear los movimientos simples cuando corresponde:

```python
def _capturas_desde(self, fila, columna):
    destinos = []
    for delta_fila, delta_columna in self.SALTOS_CAPTURA:
        destino = (fila + delta_fila, columna + delta_columna)
        if self.movimiento_captura_valido((fila, columna), destino):
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
```

`SALTOS_CAPTURA` es un **atributo de clase** (se define directamente dentro de `class Juego:`, no dentro de `__init__`), porque es un dato fijo que no cambia entre partidas ni entre objetos: `[(-2, -2), (-2, 2), (2, -2), (2, 2)]` son las cuatro direcciones diagonales posibles para saltar de a dos casillas. A diferencia de un atributo de instancia (`self.algo`), un atributo de clase se define una sola vez y lo comparten todos los objetos `Juego` que se creen.

Dentro de `movimiento_valido`, después de confirmar que hay una ficha propia en el origen, se agrega:

```python
if self.hay_captura_disponible():
    return False
```

Esto hace que, apenas exista una captura posible en cualquier parte del tablero para el jugador de turno, cualquier intento de movimiento simple sea rechazado — obligándolo a jugar la captura.

### Regla faltante 2: capturas múltiples encadenadas

Si después de comer una ficha, la misma ficha que acaba de capturar puede volver a capturar otra, en damas oficiales está obligada a seguir capturando en el mismo turno, sin pasarle el turno al rival todavía.

**Implementación:** `jugar_turno` ahora, después de ejecutar una captura, revisa si esa misma ficha (ya en su nueva posición) tiene otra captura disponible, y devuelve un resultado distinto según el caso:

```python
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
```

Antes, esta función devolvía `True` o `False`. Ahora devuelve un **texto que describe qué pasó** (`"invalido"`, `"cambiar_turno"`, `"continuar_turno"`), porque con dos reglas nuevas ya no alcanza con un simple sí/no: el resto del programa necesita distinguir entre "la jugada falló", "la jugada terminó el turno" y "la jugada debe continuar con la misma ficha".

El bucle `jugar()` usa ese resultado para, en vez de pasar el turno, obligar a que la próxima jugada salga de la misma casilla donde terminó la captura:

```python
def jugar(self):
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
```

`origen_forzado` es una variable local del método `jugar` (no un atributo de `self`, porque solo tiene sentido mientras dura esa partida específica). Cuando vale `None`, se le pide al jugador que elija libremente su ficha. Cuando tiene un valor, significa "seguís obligado a jugar con esta ficha", y el programa ni siquiera pregunta el origen: lo usa directamente.

**Nota de diseño:** si una ficha corona (se convierte en dama) en medio de una cadena de capturas, en esta versión puede seguir capturando en el mismo turno ya como dama. Es una simplificación pedagógica; algunas reglas oficiales de damas cortan el turno apenas una ficha corona, aunque pudiera seguir capturando. Vale la pena mencionarlo en clase como una decisión de diseño, no como un error.

### Regla faltante 3: perder por bloqueo (sin movimientos posibles)

Antes, la única forma de ganar era dejar al rival sin fichas. Pero en damas también se pierde si, en tu turno, no tenés **ningún** movimiento legal disponible (todas tus fichas están bloqueadas), aunque todavía tengas fichas en el tablero.

```python
def _movimientos_simples_desde(self, fila, columna):
    destinos = []
    for delta_fila, delta_columna in self.SALTOS_SIMPLES:
        destino = (fila + delta_fila, columna + delta_columna)
        if self.movimiento_valido((fila, columna), destino):
            destinos.append(destino)
    return destinos

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
```

Esta función recorre todas las fichas del jugador de turno y, para cada una, revisa si tiene alguna captura o algún movimiento simple disponible (reutilizando `_capturas_desde` y el nuevo `_movimientos_simples_desde`, que sigue el mismo patrón). Apenas encuentra una jugada posible para cualquier ficha, devuelve `True` de inmediato — no hace falta seguir revisando el resto del tablero. Se llama al principio de cada vuelta del bucle `jugar()`, antes de pedir la jugada; si da `False`, la partida termina ahí mismo con la victoria del rival.

### Programa completo, versión final (sin bugs, con reglas completas)

```python
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
    jugador_blanco = Jugador("Ana", "blanco")
    jugador_negro = Jugador("Luis", "negro")
    juego = Juego(jugador_blanco, jugador_negro)
    juego.jugar()
```

### Qué queda deliberadamente fuera de esta versión

- Captura obligatoria priorizando la jugada que coma **más** fichas (en algunas reglas oficiales, si hay varias capturas posibles, hay que elegir la que come más piezas). Acá se acepta cualquier captura disponible, no necesariamente la óptima.
- Reglas distintas de captura para fichas normales vs. damas (en algunas variantes, una ficha normal no puede capturar hacia atrás). En esta versión, tanto fichas como damas capturan en las cuatro diagonales.
- Empate por repetición de jugadas o límite de turnos sin capturas.

Estas quedan como posibles extensiones futuras, ya con la base sólida y sin bugs.

## Cierre: qué queda para seguir avanzando

Con esta base ya es natural seguir extendiendo el proyecto usando las mismas herramientas de POO: por ejemplo, crear una clase `Regla` o `ValidadorDeMovimiento` separada de `Juego` para las reglas más avanzadas (captura obligatoria, capturas múltiples), o una clase `HistorialDePartida` que registre cada jugada. La estructura en clases hace que cada una de esas mejoras se pueda agregar como una pieza nueva, sin tener que reescribir lo que ya funciona.
