# compresion con zlib y gzip para comparar con la entropia y con huffman
import zlib
import gzip

# niveles de compresion que vamos a probar
NIVELES = [1, 6, 9]


def tamano_zlib(datos, nivel):
    """Devuelve cuantos bytes ocupa el texto comprimido con zlib."""
    comprimido = zlib.compress(datos, nivel)
    return len(comprimido)


def tamano_gzip(datos, nivel):
    """Devuelve cuantos bytes ocupa el texto comprimido con gzip."""
    # mtime=0 para que siempre salga igual (no mete la fecha)
    comprimido = gzip.compress(datos, compresslevel=nivel, mtime=0)
    return len(comprimido)


def a_bytes_original(texto):
    """Pasa el texto original a bytes tal cual (utf-8)."""
    return texto.encode("utf-8")


def a_bytes_normalizado(texto):
    """Pasa el texto normalizado a bytes con latin-1."""
    # usamos latin-1 para que cada simbolo (incluida la ñ) ocupe 1 solo byte
    # en utf-8 la ñ ocuparia 2 bytes y eso no seria justo
    return texto.encode("latin-1")


def bits_por_caracter(bytes_comprimidos, num_caracteres):
    """Bits por caracter del texto comprimido."""
    return 8 * bytes_comprimidos / num_caracteres


def razon_compresion(tamano_original, tamano_comprimido):
    """Cuantas veces mas pequeño quedo el archivo."""
    return tamano_original / tamano_comprimido
