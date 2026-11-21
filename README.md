# Entropia y compresion de texto

Proyecto para la materia: medimos la entropia de varios textos (H1, H2, H3, entropias
condicionales F2 y F3, redundancia) y la comparamos con lo que logran Huffman (hecho a mano),
zlib y gzip.

Textos usados:

- `quijote`: Don Quijote (Gutenberg 2000, espanol)
- `niebla`: Niebla de Unamuno (Gutenberg 49836, espanol)
- `pride`: Pride and Prejudice (Gutenberg 1342, ingles)
- `codigo`: archivos `.py` de la biblioteca estandar de Python pegados
- `aleatorio`: 200000 simbolos al azar equiprobables de los 28 del alfabeto (semilla 42)

## Como correrlo

Se necesita [uv](https://docs.astral.sh/uv/). No usa librerias externas, solo la estandar.

```
uv run main.py      # descarga los textos (la primera vez) y saca todos los resultados
uv run pruebas.py   # pruebas sencillas, debe decir "todas las pruebas pasaron"
```

Los textos quedan en `datos/` y los resultados en `resultados/resultados.txt` y
`resultados/resultados.csv`.

## Notas

- La version de Python esta fijada en 3.13 (archivo `.python-version`, hecho con `uv python pin 3.13`).
  El texto `codigo` sale de los `.py` de la biblioteca estandar, asi que con otra version de Python
  saldria otro texto y otros numeros.
- En la parte de sesgo por tamano finito los fragmentos son el inicio de cada libro. H3 tiende a
  crecer con N, pero como el libro no es igual en todas partes puede bajar un poquito entre 50000
  y 100000 (pasa en `niebla` y `pride`).
- El tamano de Huffman cuenta los bits empaquetados, la tabla de codigos y una cabecera de 5 bytes
  (cuantos bits hay y cuantos simbolos tiene la tabla), que es lo que necesitaria el decodificador.
- Las ligaduras (œ, æ, ß) se cambian por dos letras al normalizar (manœuvre -> manoeuvre).

## Que hace cada archivo

- `normalizar.py`: pasa el texto a minusculas, quita tildes (deja la ñ) y deja solo las 27 letras y el espacio.
- `corpus.py`: descarga los libros de Gutenberg, junta el codigo Python y genera el texto aleatorio.
- `entropia.py`: cuenta bloques de n letras y calcula las entropias y la redundancia.
- `huffman.py`: arbol de Huffman, codificar, empaquetar en bytes, decodificar, longitud media.
- `compresion.py`: tamanos con zlib y gzip, bits por caracter y razon de compresion.
- `main.py`: junta todo e imprime las tablas.
- `pruebas.py`: pruebas con assert.
