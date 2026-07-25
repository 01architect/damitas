# Proyecto: Juego de Damas — De la Lógica de Programación a un Juego Jugable

Este proyecto arma, paso a paso, un juego de damas por consola en Python. Cada paso agrega una sola idea nueva y reutiliza exactamente lo que ya se vio en clase: arreglos bidimensionales, `for`, `if`. El objetivo no es llegar de una vez al juego completo, sino que cada entrega intermedia ya funcione y se entienda por completo antes de seguir.

## Reglas simplificadas que vamos a programar

Para no complicar el proyecto con todo el reglamento oficial de damas, trabajamos con una versión reducida:

- Tablero de 8x8, pero solo se usan las casillas oscuras (32 casillas), como en el juego real.
- Jugador 1 empieza abajo y se mueve hacia arriba; jugador 2 empieza arriba y se mueve hacia abajo.
- Una ficha normal se mueve una casilla en diagonal, solo hacia adelante.
- Se captura saltando en diagonal sobre una ficha rival hacia una casilla vacía.
- Al llegar a la última fila del lado contrario, la ficha se corona (se convierte en dama y puede moverse en ambas direcciones).
- No implementamos captura obligatoria ni saltos múltiples en un mismo turno — son mejoras que quedan planteadas al final para una segunda versión.

## Paso 1: Representar el tablero como arreglo bidimensional

El tablero es una matriz de 8x8, igual que los ejemplos que ya vimos. Usamos números para representar qué hay en cada casilla:

- `0` = casilla vacía
- `1` = ficha del jugador 1
- `2` = ficha del jugador 2
- `3` = dama del jugador 1
- `4` = dama del jugador 2

```python
def crear_tablero():
    tablero = []
    for fila in range(8):
        fila_actual = []
        for columna in range(8):
            if (fila + columna) % 2 == 1:      # solo casillas oscuras
                if fila < 3:
                    fila_actual.append(2)      # fichas del jugador 2, arriba
                elif fila > 4:
                    fila_actual.append(1)      # fichas del jugador 1, abajo
                else:
                    fila_actual.append(0)      # casilla oscura vacía (centro)
            else:
                fila_actual.append(0)          # casilla clara, no se usa nunca
        tablero.append(fila_actual)
    return tablero
```

**Por qué así:**
- `def crear_tablero():` define una función. La usamos porque vamos a necesitar el tablero cada vez que empiece una partida, y una función evita repetir el mismo bloque de código.
- El `for fila` externo y el `for columna` interno recorren las 8x8 = 64 casillas, exactamente como en el ejemplo de la tabla de multiplicar.
- `(fila + columna) % 2 == 1` es el truco clásico para identificar casillas oscuras: el operador `%` (módulo) da el resto de una división. Si la suma de fila y columna es impar, esa casilla es oscura.
- Se arma primero `fila_actual` (un arreglo de una sola fila) y al final se agrega a `tablero` con `.append()`. Es el mismo patrón que usamos en la tabla de multiplicar: primero se construye la fila completa, después se agrega a la matriz.
- La función `return tablero` entrega el arreglo ya armado para que el resto del programa lo use.

## Paso 2: Imprimir el tablero de forma legible

```python
def imprimir_tablero(tablero):
    simbolos = {0: ".", 1: "o", 2: "x", 3: "O", 4: "X"}
    print("   " + " ".join(str(c) for c in range(8)))
    for fila in range(8):
        fichas_fila = [simbolos[tablero[fila][col]] for col in range(8)]
        print(fila, " ", " ".join(fichas_fila))
```

**Por qué así:**
- `simbolos` es un diccionario que traduce cada número del tablero a un carácter más fácil de leer (`.` vacío, `o`/`O` fichas del jugador 1, `x`/`X` fichas del jugador 2). Los estudiantes ya conocen `if`/`for`; el diccionario es solo una tabla de traducción, se puede reemplazar por una cadena de `if` si se prefiere no introducirlo todavía.
- `[simbolos[tablero[fila][col]] for col in range(8)]` es una lista por comprensión: es exactamente lo mismo que escribir un `for` que arma una lista, pero en una sola línea. Equivale a:
  ```python
  fichas_fila = []
  for col in range(8):
      fichas_fila.append(simbolos[tablero[fila][col]])
  ```
- `" ".join(...)` une los elementos de una lista en un solo texto, separados por espacios, para que se vea como una fila del tablero y no como una lista de Python.

## Paso 3: Mover una ficha (todavía sin validar)

Antes de agregar reglas, conviene programar el movimiento "en bruto": tomar lo que hay en una casilla y ponerlo en otra.

```python
def mover(tablero, origen, destino):
    fila_o, col_o = origen
    fila_d, col_d = destino
    tablero[fila_d][col_d] = tablero[fila_o][col_o]
    tablero[fila_o][col_o] = 0
```

**Por qué así:**
- `origen` y `destino` son tuplas, por ejemplo `(5, 0)`. Una tupla agrupa dos valores relacionados (fila y columna) en una sola variable, para no tener que pasar cuatro parámetros sueltos a la función.
- `fila_o, col_o = origen` desempaqueta la tupla en dos variables independientes de una sola vez.
- La lógica del movimiento son dos líneas: primero se copia el valor de la casilla de origen hacia la casilla destino, después se vacía (`= 0`) la casilla de origen. Si se hiciera al revés, se perdería el valor antes de copiarlo.

## Paso 4: Validar el movimiento con `if`

Un movimiento normal (sin captura) debe cumplir varias condiciones. Usamos una función que devuelve `True` o `False`.

```python
def movimiento_valido(tablero, origen, destino, turno):
    fila_o, col_o = origen
    fila_d, col_d = destino

    if not (0 <= fila_d < 8 and 0 <= col_d < 8):
        return False                       # el destino debe estar dentro del tablero
    if tablero[fila_d][col_d] != 0:
        return False                       # el destino debe estar vacío

    ficha = tablero[fila_o][col_o]
    if ficha == 0:
        return False                       # no se puede mover una casilla vacía
    if turno == 1 and ficha not in (1, 3):
        return False                       # la ficha debe ser del jugador que juega
    if turno == 2 and ficha not in (2, 4):
        return False

    diferencia_fila = fila_d - fila_o
    diferencia_col = abs(col_d - col_o)

    if abs(diferencia_fila) != 1 or diferencia_col != 1:
        return False                       # debe moverse exactamente 1 casilla en diagonal

    es_dama = ficha in (3, 4)
    if not es_dama:
        if turno == 1 and diferencia_fila != -1:
            return False                   # jugador 1 solo avanza hacia arriba
        if turno == 2 and diferencia_fila != 1:
            return False                   # jugador 2 solo avanza hacia abajo

    return True
```

**Por qué así:**
- Cada `if` revisa una sola regla y corta con `return False` apenas algo falla. Es más fácil de leer que un único `if` gigante con muchos `and`, y facilita ir agregando reglas de a una.
- `0 <= fila_d < 8` es una comparación encadenada de Python: revisa que `fila_d` esté entre 0 y 7 en una sola expresión.
- `ficha not in (1, 3)` pregunta si el valor de `ficha` no está dentro de esa tupla de valores posibles. Sirve para verificar "es una ficha mía" sin escribir dos `if` separados (`!= 1` y `!= 3`).
- `abs(diferencia_fila)` calcula el valor absoluto (sin signo). Nos interesa saber si la ficha se movió 1 fila de distancia, sin importar si fue hacia arriba o hacia abajo; por eso se compara `abs(diferencia_fila) != 1`.
- El signo de `diferencia_fila` (positivo o negativo) sí importa para saber la dirección: por eso, para las fichas normales (`es_dama == False`), se revisa el signo exacto según el turno.

## Paso 5: Capturar fichas (comer)

Capturar es parecido a moverse, pero saltando 2 casillas y quitando la ficha rival que quedó en el medio.

```python
def movimiento_captura_valido(tablero, origen, destino, turno):
    fila_o, col_o = origen
    fila_d, col_d = destino

    if not (0 <= fila_d < 8 and 0 <= col_d < 8):
        return False
    if tablero[fila_d][col_d] != 0:
        return False

    diferencia_fila = fila_d - fila_o
    diferencia_col = abs(col_d - col_o)

    if abs(diferencia_fila) != 2 or diferencia_col != 2:
        return False                        # una captura salta exactamente 2 casillas

    fila_media = (fila_o + fila_d) // 2
    col_media = (col_o + col_d) // 2
    ficha_intermedia = tablero[fila_media][col_media]

    if turno == 1 and ficha_intermedia not in (2, 4):
        return False                        # en el medio debe haber una ficha rival
    if turno == 2 and ficha_intermedia not in (1, 3):
        return False

    return True


def capturar(tablero, origen, destino):
    fila_o, col_o = origen
    fila_d, col_d = destino
    fila_media = (fila_o + fila_d) // 2
    col_media = (col_o + col_d) // 2

    tablero[fila_media][col_media] = 0       # se elimina la ficha comida
    mover(tablero, origen, destino)          # reutilizamos la función del paso 3
```

**Por qué así:**
- `//` es la división entera: divide y descarta la parte decimal. Si origen es fila 5 y destino es fila 3, `(5 + 3) // 2` da 4, que es exactamente la fila que está en el medio de las dos. Lo mismo para la columna. Así se calcula la casilla intermedia sin necesidad de un `for`.
- `capturar` no repite la lógica de mover: llama a `mover(tablero, origen, destino)`, la misma función del paso 3. Reutilizar funciones ya hechas evita duplicar código y errores.
- Separar "¿es válida la captura?" (`movimiento_captura_valido`) de "ejecutar la captura" (`capturar`) sigue el mismo patrón que ya usamos con `movimiento_valido` y `mover`: primero se pregunta, después se actúa.

## Paso 6: Coronar una ficha (convertirla en dama)

```python
def coronar(tablero, destino, turno):
    fila_d, col_d = destino
    if turno == 1 and fila_d == 0:
        tablero[fila_d][col_d] = 3     # ficha del jugador 1 llega arriba -> dama
    if turno == 2 and fila_d == 7:
        tablero[fila_d][col_d] = 4     # ficha del jugador 2 llega abajo -> dama
```

**Por qué así:**
- Esta función se llama después de cada movimiento o captura exitosa. Solo revisa una cosa: si la ficha llegó a la última fila del lado contrario, cambia su valor en el arreglo (de 1 a 3, o de 2 a 4). No hace falta crear una ficha nueva, solo se sobrescribe el número guardado en esa posición del tablero.

## Paso 7: Alternar turnos y armar el bucle principal

Hasta acá tenemos piezas sueltas (funciones). Ahora se ensamblan en un bucle que repite: mostrar tablero, pedir jugada, validar, mover, cambiar de turno.

```python
def jugar():
    tablero = crear_tablero()
    turno = 1

    while True:
        imprimir_tablero(tablero)
        print(f"Turno del jugador {turno}")

        entrada_origen = input("Fila y columna de origen (ej: 5 0): ")
        entrada_destino = input("Fila y columna de destino (ej: 4 1): ")

        fila_o, col_o = map(int, entrada_origen.split())
        fila_d, col_d = map(int, entrada_destino.split())
        origen = (fila_o, col_o)
        destino = (fila_d, col_d)

        if movimiento_captura_valido(tablero, origen, destino, turno):
            capturar(tablero, origen, destino)
            coronar(tablero, destino, turno)
        elif movimiento_valido(tablero, origen, destino, turno):
            mover(tablero, origen, destino)
            coronar(tablero, destino, turno)
        else:
            print("Movimiento inválido, intenta de nuevo.")
            continue

        turno = 2 if turno == 1 else 1
```

**Por qué así:**
- `while True:` crea un bucle que se repite indefinidamente. Es distinto al `for`, que recorre un arreglo con cantidad conocida de vueltas; acá no sabemos de antemano cuántos turnos va a durar la partida, así que se usa `while` y se corta más adelante con `break` (paso 8).
- `input(...)` pide texto al usuario. `entrada_origen.split()` separa ese texto en partes usando el espacio como separador (por ejemplo `"5 0"` se convierte en `["5", "0"]`). `map(int, ...)` aplica la función `int()` a cada parte de esa lista, convirtiendo texto en números.
- Se prueba primero si el movimiento es una captura válida, y si no, si es un movimiento simple válido. El orden importa: una jugada de captura nunca sería aceptada por `movimiento_valido` (porque salta 2 casillas, no 1), así que no hay conflicto entre ambas funciones.
- `continue` vuelve al inicio del `while` sin ejecutar el resto del bloque, es decir, sin cambiar de turno: si la jugada fue inválida, le toca intentar de nuevo al mismo jugador.
- `turno = 2 if turno == 1 else 1` es un `if` en una sola línea (operador ternario): "si el turno actual es 1, pasa a ser 2; si no, pasa a ser 1". Alterna entre los dos jugadores en cada vuelta exitosa del bucle.

## Paso 8: Detectar el ganador

```python
def contar_fichas(tablero, turno):
    contador = 0
    for fila in range(8):
        for columna in range(8):
            valor = tablero[fila][columna]
            if turno == 1 and valor in (1, 3):
                contador += 1
            if turno == 2 and valor in (2, 4):
                contador += 1
    return contador
```

Y se agrega la verificación dentro del bucle principal, justo después de cambiar de turno:

```python
        rival = 2 if turno == 1 else 1
        if contar_fichas(tablero, rival) == 0:
            imprimir_tablero(tablero)
            print(f"¡El jugador {turno} gana la partida!")
            break
```

**Por qué así:**
- `contar_fichas` recorre todo el tablero (`for` doble, igual que en el paso 1) y cuenta cuántas fichas le quedan a un jugador. Se reutiliza esta misma función para cualquiera de los dos jugadores, pasando `turno` como parámetro.
- Después de mover, se calcula quién es el `rival` del jugador que acaba de jugar. Si al rival ya no le quedan fichas (`contar_fichas(...) == 0`), la partida terminó.
- `break` corta el `while True`, deteniendo el juego apenas se cumple la condición de victoria.

## Programa completo

Uniendo todos los pasos anteriores, este es el juego funcionando de punta a punta:

```python
def crear_tablero():
    tablero = []
    for fila in range(8):
        fila_actual = []
        for columna in range(8):
            if (fila + columna) % 2 == 1:
                if fila < 3:
                    fila_actual.append(2)
                elif fila > 4:
                    fila_actual.append(1)
                else:
                    fila_actual.append(0)
            else:
                fila_actual.append(0)
        tablero.append(fila_actual)
    return tablero


def imprimir_tablero(tablero):
    simbolos = {0: ".", 1: "o", 2: "x", 3: "O", 4: "X"}
    print("   " + " ".join(str(c) for c in range(8)))
    for fila in range(8):
        fichas_fila = [simbolos[tablero[fila][col]] for col in range(8)]
        print(fila, " ", " ".join(fichas_fila))


def mover(tablero, origen, destino):
    fila_o, col_o = origen
    fila_d, col_d = destino
    tablero[fila_d][col_d] = tablero[fila_o][col_o]
    tablero[fila_o][col_o] = 0


def movimiento_valido(tablero, origen, destino, turno):
    fila_o, col_o = origen
    fila_d, col_d = destino

    if not (0 <= fila_d < 8 and 0 <= col_d < 8):
        return False
    if tablero[fila_d][col_d] != 0:
        return False

    ficha = tablero[fila_o][col_o]
    if ficha == 0:
        return False
    if turno == 1 and ficha not in (1, 3):
        return False
    if turno == 2 and ficha not in (2, 4):
        return False

    diferencia_fila = fila_d - fila_o
    diferencia_col = abs(col_d - col_o)

    if abs(diferencia_fila) != 1 or diferencia_col != 1:
        return False

    es_dama = ficha in (3, 4)
    if not es_dama:
        if turno == 1 and diferencia_fila != -1:
            return False
        if turno == 2 and diferencia_fila != 1:
            return False

    return True


def movimiento_captura_valido(tablero, origen, destino, turno):
    fila_o, col_o = origen
    fila_d, col_d = destino

    if not (0 <= fila_d < 8 and 0 <= col_d < 8):
        return False
    if tablero[fila_d][col_d] != 0:
        return False

    diferencia_fila = fila_d - fila_o
    diferencia_col = abs(col_d - col_o)

    if abs(diferencia_fila) != 2 or diferencia_col != 2:
        return False

    fila_media = (fila_o + fila_d) // 2
    col_media = (col_o + col_d) // 2
    ficha_intermedia = tablero[fila_media][col_media]

    if turno == 1 and ficha_intermedia not in (2, 4):
        return False
    if turno == 2 and ficha_intermedia not in (1, 3):
        return False

    return True


def capturar(tablero, origen, destino):
    fila_o, col_o = origen
    fila_d, col_d = destino
    fila_media = (fila_o + fila_d) // 2
    col_media = (col_o + col_d) // 2

    tablero[fila_media][col_media] = 0
    mover(tablero, origen, destino)


def coronar(tablero, destino, turno):
    fila_d, col_d = destino
    if turno == 1 and fila_d == 0:
        tablero[fila_d][col_d] = 3
    if turno == 2 and fila_d == 7:
        tablero[fila_d][col_d] = 4


def contar_fichas(tablero, turno):
    contador = 0
    for fila in range(8):
        for columna in range(8):
            valor = tablero[fila][columna]
            if turno == 1 and valor in (1, 3):
                contador += 1
            if turno == 2 and valor in (2, 4):
                contador += 1
    return contador


def jugar():
    tablero = crear_tablero()
    turno = 1

    while True:
        imprimir_tablero(tablero)
        print(f"Turno del jugador {turno}")

        entrada_origen = input("Fila y columna de origen (ej: 5 0): ")
        entrada_destino = input("Fila y columna de destino (ej: 4 1): ")

        fila_o, col_o = map(int, entrada_origen.split())
        fila_d, col_d = map(int, entrada_destino.split())
        origen = (fila_o, col_o)
        destino = (fila_d, col_d)

        if movimiento_captura_valido(tablero, origen, destino, turno):
            capturar(tablero, origen, destino)
            coronar(tablero, destino, turno)
        elif movimiento_valido(tablero, origen, destino, turno):
            mover(tablero, origen, destino)
            coronar(tablero, destino, turno)
        else:
            print("Movimiento inválido, intenta de nuevo.")
            continue

        rival = 2 if turno == 1 else 1
        if contar_fichas(tablero, rival) == 0:
            imprimir_tablero(tablero)
            print(f"¡El jugador {turno} gana la partida!")
            break

        turno = 2 if turno == 1 else 1


jugar()
```

## Qué le falta a esta versión (a propósito)

Quedó simplificada así a propósito, para que el foco siga siendo arreglos, `for` e `if`:

- No obliga a capturar cuando hay una captura disponible (regla oficial de damas).
- No permite capturas múltiples encadenadas en un mismo turno.
- No valida que el jugador esté eligiendo realmente una de sus propias fichas antes de pedir el destino (se detecta recién dentro de `movimiento_valido`).
- No hay interfaz gráfica, todo es texto por consola.

Todas estas son buenas siguientes tareas una vez que el grupo domine esta versión base.

## Por qué este proyecto es el puente perfecto hacia POO

En esta versión, `tablero` y `turno` viajan como parámetros por casi todas las funciones (`mover(tablero, ...)`, `movimiento_valido(tablero, ..., turno)`, `contar_fichas(tablero, turno)`...). Funciona bien con un tablero y dos jugadores, pero ya se nota el patrón: muchas funciones necesitan los mismos datos dando vueltas.

Con Programación Orientada a Objetos, esas mismas funciones se agruparían dentro de una clase `Tablero`, que guardaría el arreglo internamente (`self.casillas`) y ofrecería métodos como `tablero.mover(origen, destino)` o `tablero.contar_fichas(turno)`, sin tener que pasar `tablero` una y otra vez como parámetro. Una clase `Ficha` podría guardar su propio color y si es dama o no, en vez de codificarlo todo con números (1, 2, 3, 4) sueltos en el arreglo.

La idea para la siguiente etapa del curso: mostrar que el arreglo bidimensional no desaparece con la POO, simplemente pasa a vivir "adentro" de un objeto, y las funciones sueltas se convierten en métodos de ese objeto. Por eso conviene terminar bien esta versión con funciones y arreglos antes de dar el salto.
