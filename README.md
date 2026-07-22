# Proyecto de Damas — Lógica + POO + Interfaz Gráfica

Juego de damas en Python, pensado como proyecto de demostración para el curso de Lógica de Programación. Reglas completas (captura obligatoria, capturas encadenadas, coronación, victoria por fichas o por bloqueo) e interfaz gráfica con hover, resaltado de movimientos válidos y arrastrar-y-soltar.

## Archivos del proyecto

| Archivo | Qué contiene |
|---|---|
| `logica_damas.py` | El modelo del juego: clases `Ficha`, `Dama`, `Tablero`, `Jugador`, `Juego`. Todas las reglas viven acá. No sabe nada de ventanas ni de mouse. |
| `interfaz_damas.py` | La ventana gráfica (Tkinter). Dibuja el tablero, escucha el mouse y llama a los métodos ya construidos en `logica_damas.py`. No define ninguna regla nueva. |

Los dos archivos deben estar **en la misma carpeta**, porque `interfaz_damas.py` importa las clases desde `logica_damas.py`.

## Requisitos

- Python 3.8 o superior.
- Tkinter, que ya viene incluido con Python en Windows y macOS. En algunas distribuciones de Linux hay que instalarlo aparte (por ejemplo `sudo apt install python3-tk` en Ubuntu/Debian). No hace falta instalar nada con `pip`.

## Cómo ejecutarlo

**Interfaz gráfica (recomendado):**

```
python interfaz_damas.py
```

Se abre una ventana con el tablero de 8x8 ya armado con las fichas iniciales.

**Solo la lógica, por consola (para probar las reglas sin ventana):**

```
python logica_damas.py
```

Pide las jugadas escribiendo fila y columna separadas por un espacio (por ejemplo `5 0`).

## Controles de la interfaz gráfica

- **Pasar el mouse** sobre una casilla la resalta (efecto hover).
- **Clic sobre una ficha propia**: la selecciona (se marca en amarillo) y muestra en verde las casillas donde puede moverse.
- **Clic sobre una casilla destino**: mueve la ficha seleccionada ahí, si el movimiento es válido.
- **Arrastrar** (mantener apretado el clic sobre una ficha, mover el mouse y soltar sobre el destino): mueve la ficha con un efecto de desplazamiento visual, en vez de hacer dos clics separados.
- Si hay una **captura disponible**, el juego obliga a jugarla (no deja hacer un movimiento simple mientras exista una captura posible).
- Si una ficha **captura y puede seguir capturando** con el mismo salto, queda seleccionada automáticamente para continuar la cadena, sin pasar el turno.
- Cuando una ficha llega a la última fila del lado contrario, **corona** (se convierte en dama, se dibuja con borde dorado) y a partir de ahí se mueve en ambas direcciones.
- La partida termina cuando un jugador se queda sin fichas, o cuando le toca jugar y no tiene ningún movimiento posible.

## Reglas simplificadas a propósito

Para mantener el proyecto enfocado en lógica de programación y no en el reglamento completo de damas, quedaron afuera (a propósito):

- Elegir automáticamente la captura que come más fichas cuando hay varias disponibles (acá se acepta cualquier captura válida).
- Reglas de captura distintas para fichas normales y damas (en esta versión, ambas capturan en las cuatro diagonales).
- Empate por repetición de jugadas o límite de turnos sin capturas.

## Estructura interna (resumen)

- `Ficha` / `Dama`: cada ficha es un objeto con su color y posición. `Dama` hereda de `Ficha` y sobrescribe cómo decide si una dirección de movimiento es válida (polimorfismo).
- `Tablero`: guarda la matriz 8x8 de forma encapsulada (`_casillas`) y expone métodos públicos (`obtener_ficha`, `mover_ficha`, `contar_fichas`, etc.) para que el resto del programa no necesite tocar la matriz directamente.
- `Jugador`: nombre y color de cada participante.
- `Juego`: conoce las reglas (movimiento, captura obligatoria, capturas encadenadas, coronación, victoria) y coordina el turno. Tanto la consola (`jugar()`) como la interfaz gráfica (`InterfazDamas`) usan exactamente los mismos métodos de esta clase.
- `InterfazDamas` (en `interfaz_damas.py`): traduce eventos del mouse (`<Motion>`, `<ButtonPress-1>`, `<B1-Motion>`, `<ButtonRelease-1>`) en llamadas a `Juego`, y dibuja el estado actual del tablero. No contiene reglas del juego.
