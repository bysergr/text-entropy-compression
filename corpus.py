# descarga y preparacion de los textos que vamos a analizar
import os
import random
import shutil
import urllib.request

from normalizar import ALFABETO

# ids de Project Gutenberg (quijote y niebla en espanol, pride en ingles)
LIBROS = {"quijote": 2000, "niebla": 49836, "pride": 1342}

# usamos el espejo porque gutenberg.org a veces da error 503
URL = "https://gutenberg.pglaf.org/cache/epub/{id}/pg{id}.txt"

# carpeta datos/ junto a este archivo
CARPETA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")


def quitar_encabezado(texto):
    """Deja solo el texto entre las marcas START y END de Gutenberg."""
    lineas = texto.split("\n")
    inicio = 0
    fin = len(lineas)
    # buscamos donde empieza y donde termina el libro
    for i in range(len(lineas)):
        if "*** START OF" in lineas[i]:
            inicio = i + 1
        if "*** END OF" in lineas[i]:
            fin = i
            break
    return "\n".join(lineas[inicio:fin])


def descargar_libro(nombre, id_libro):
    """Descarga un libro de Gutenberg y lo guarda en datos/."""
    ruta = os.path.join(CARPETA_DATOS, nombre + ".txt")
    # si ya lo tenemos no lo bajamos otra vez
    if os.path.exists(ruta):
        print(f"{nombre}: ya estaba descargado")
        return

    url = URL.format(id=id_libro)
    print(f"descargando {nombre} de {url} ...")
    peticion = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    respuesta = urllib.request.urlopen(peticion)
    datos = respuesta.read()

    # pasamos a texto y quitamos el BOM si viene
    texto = datos.decode("utf-8")
    if texto.startswith("\ufeff"):
        texto = texto[1:]

    texto = quitar_encabezado(texto)

    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(texto)
    print(f"{nombre}: guardado con {len(texto)} caracteres")


def juntar_codigo_python(minimo=100000):
    """Junta archivos .py de la biblioteca estandar en datos/codigo.txt."""
    ruta = os.path.join(CARPETA_DATOS, "codigo.txt")
    if os.path.exists(ruta):
        print("codigo: ya estaba listo")
        return

    carpeta_codigo = os.path.join(CARPETA_DATOS, "codigo")
    os.makedirs(carpeta_codigo, exist_ok=True)

    # la carpeta donde esta la biblioteca estandar
    carpeta_lib = os.path.dirname(os.__file__)

    # archivos .py en orden alfabetico para que siempre salga igual
    archivos = []
    for nombre in os.listdir(carpeta_lib):
        if nombre.endswith(".py"):
            archivos.append(nombre)
    archivos.sort()

    # vamos pegando archivos hasta tener suficientes caracteres
    partes = []
    total = 0
    for nombre in archivos:
        origen = os.path.join(carpeta_lib, nombre)
        with open(origen, "r", encoding="utf-8", newline="") as f:
            contenido = f.read()
        shutil.copy(origen, os.path.join(carpeta_codigo, nombre))
        partes.append(contenido)
        total = total + len(contenido)
        if total >= minimo:
            break

    texto = "".join(partes)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(texto)
    print(f"codigo: {len(partes)} archivos, {len(texto)} caracteres")


def generar_aleatorio(n=200000, semilla=42):
    """Genera n simbolos al azar equiprobables del ALFABETO."""
    ruta = os.path.join(CARPETA_DATOS, "aleatorio.txt")
    if os.path.exists(ruta):
        print("aleatorio: ya estaba generado")
        return

    # con la semilla fija siempre sale la misma secuencia
    random.seed(semilla)
    simbolos = []
    for i in range(n):
        simbolos.append(random.choice(ALFABETO))
    texto = "".join(simbolos)

    with open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(texto)
    print(f"aleatorio: generado con {len(texto)} simbolos")


def preparar_corpus():
    """Descarga y genera todos los textos."""
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    for nombre in LIBROS:
        descargar_libro(nombre, LIBROS[nombre])
    # pedimos 150000 para que el normalizado tambien pase de 100000
    juntar_codigo_python(150000)
    generar_aleatorio()


def cargar_textos():
    """Lee los textos de datos/ y los devuelve en un diccionario."""
    nombres = ["quijote", "niebla", "pride", "codigo", "aleatorio"]
    textos = {}
    for nombre in nombres:
        ruta = os.path.join(CARPETA_DATOS, nombre + ".txt")
        with open(ruta, "r", encoding="utf-8", newline="") as f:
            textos[nombre] = f.read()
    return textos
