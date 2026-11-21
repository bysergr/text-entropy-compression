# pruebas sencillas de los modulos (se corre con: uv run pruebas.py)
import math

from normalizar import normalizar, ALFABETO
from corpus import quitar_encabezado
from entropia import contar_bloques, entropia_conjunta, calcular_entropias, HMAX
import huffman
import compresion


# ---- normalizar ----
assert len(ALFABETO) == 28
assert normalizar("¡Hola, Señor!") == "hola señor"
assert normalizar("ÁÉÍÓÚ ü Ñ") == "aeiou u ñ"
assert normalizar("  muchos   espacios\n\ny 123 numeros  ") == "muchos espacios y numeros"
assert normalizar("pingüino") == "pinguino"
assert normalizar("manœuvre") == "manoeuvre"
# todo lo que sale tiene que estar en el alfabeto
for c in normalizar("Él dijo: «¿qué tal?» — 42 años."):
    assert c in ALFABETO

# ---- corpus ----
libro = "basura\n*** START OF THE BOOK ***\nhola\nmundo\n*** END OF THE BOOK ***\nmas basura"
assert quitar_encabezado(libro) == "hola\nmundo"

# ---- entropia ----
conteo = contar_bloques("abab", 2)
assert conteo == {"ab": 2, "ba": 1}
assert entropia_conjunta("aaaa", 1) == 0.0
assert abs(entropia_conjunta("abab", 1) - 1.0) < 1e-9
assert abs(entropia_conjunta("abcd", 1) - 2.0) < 1e-9
assert abs(HMAX - math.log2(28)) < 1e-9
e = calcular_entropias("el perro de san roque no tiene rabo")
assert e["H1"] >= e["H2"] >= e["H3"]
assert e["F2"] <= e["H2"]
assert 0 <= e["R1"] <= 1

# ---- huffman ----
texto = "abracadabra"
frec = huffman.frecuencias(texto)
assert frec["a"] == 5
arbol = huffman.construir_arbol(frec)
codigos = huffman.generar_codigos(arbol)
bits = huffman.codificar(texto, codigos)
assert huffman.decodificar(bits, arbol) == texto
# la letra mas comun tiene el codigo mas corto
for letra in codigos:
    assert len(codigos["a"]) <= len(codigos[letra])

# empaquetar y desempaquetar deja todo igual
datos = huffman.empaquetar_bits(bits)
assert len(datos) == math.ceil(len(bits) / 8)
assert huffman.desempaquetar_bits(datos, len(bits)) == bits
assert huffman.empaquetar_bits("1") == bytes([128])

# L entre H1 y H1 + 1
h1 = entropia_conjunta(texto, 1)
L = huffman.longitud_media(codigos, frec)
assert h1 <= L < h1 + 1

# caso de un solo simbolo
frec1 = huffman.frecuencias("aaaa")
arbol1 = huffman.construir_arbol(frec1)
codigos1 = huffman.generar_codigos(arbol1)
assert codigos1 == {"a": "0"}
assert huffman.decodificar(huffman.codificar("aaaa", codigos1), arbol1) == "aaaa"

# tabla: 1 + 1 + ceil(largo/8) por simbolo
assert huffman.tamano_tabla({"a": "0", "b": "101010101"}) == (1 + 1 + 1) + (1 + 1 + 2)
# el total suma tambien la cabecera de 4 + 1 bytes
assert huffman.tamano_comprimido(bits, codigos) == len(datos) + huffman.tamano_tabla(codigos) + 5

# ---- compresion ----
assert compresion.a_bytes_normalizado("ñandu") == b"\xf1andu"
assert len(compresion.a_bytes_original("ñ")) == 2
repetido = b"hola " * 1000
assert compresion.tamano_zlib(repetido, 9) < len(repetido)
assert compresion.tamano_gzip(repetido, 9) < len(repetido)
assert compresion.bits_por_caracter(10, 80) == 1.0
assert compresion.razon_compresion(100, 25) == 4.0

print("todas las pruebas pasaron")
