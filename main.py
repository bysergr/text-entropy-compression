# programa principal: entropia y compresion de texto
import os
import csv

from normalizar import normalizar
from corpus import preparar_corpus, cargar_textos
from entropia import calcular_entropias, HMAX
import huffman
import compresion

# carpeta resultados/ junto a este archivo
CARPETA_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")

# tamanos de los fragmentos para ver el sesgo por tamano finito
FRAGMENTOS = [10000, 50000, 100000]

# aqui vamos guardando todo lo que se imprime para el .txt
lineas = []
# y aqui las filas del csv: texto, seccion, medida, valor
filas_csv = []


def escribir(linea=""):
    """Imprime una linea y la guarda para el archivo de resultados."""
    print(linea)
    lineas.append(linea)


def guardar_csv(texto, seccion, medida, valor):
    """Agrega una fila al csv."""
    filas_csv.append([texto, seccion, medida, valor])


def parte_entropias(normalizados):
    """Tabla de entropias de cada texto normalizado completo."""
    escribir("=" * 80)
    escribir("1. ENTROPIAS (texto normalizado completo, en bits por simbolo)")
    escribir(f"   Hmax = log2(28) = {HMAX:.4f}")
    escribir("=" * 80)
    # formatos de las tablas: :<10 alinea a la izquierda en 10 espacios,
    # :>9 alinea a la derecha en 9 espacios y :>7.4f ademas deja 4 decimales
    medidas = ["H1", "H2", "H3", "F2", "F3", "R1", "R3"]
    titulo = f"{'texto':<10} {'simbolos':>9}"
    for medida in medidas:
        titulo = titulo + f" {medida:>7}"
    escribir(titulo)
    entropias = {}
    for nombre in normalizados:
        texto = normalizados[nombre]
        e = calcular_entropias(texto)
        entropias[nombre] = e
        # armamos la fila columna por columna
        fila = f"{nombre:<10} {len(texto):>9}"
        for medida in medidas:
            fila = fila + f" {e[medida]:>7.4f}"
        escribir(fila)
        # guardamos cada medida en el csv
        for medida in medidas:
            guardar_csv(nombre, "entropia", medida, round(e[medida], 6))
    escribir()
    return entropias


def parte_fragmentos(normalizados):
    """Entropias con pedazos del texto de distintos tamanos."""
    escribir("=" * 80)
    escribir("2. SESGO POR TAMANO FINITO (primeros N simbolos del texto normalizado)")
    # ojo: los fragmentos son el inicio del libro, y el texto no es igual en
    # todas partes, asi que H3 tiende a crecer con N pero puede bajar un poquito
    escribir("=" * 80)
    escribir(f"{'texto':<10} {'N':>9} {'H1':>7} {'H2':>7} {'H3':>7} {'F3':>7}")
    for nombre in normalizados:
        texto = normalizados[nombre]
        for tam in FRAGMENTOS:
            # si el texto es mas corto que el fragmento no lo calculamos
            if len(texto) < tam:
                escribir(f"{nombre:<10} {tam:>9}   (texto muy corto)")
                continue
            e = calcular_entropias(texto[:tam])
            fila = f"{nombre:<10} {tam:>9}"
            fila = fila + f" {e['H1']:>7.4f} {e['H2']:>7.4f}"
            fila = fila + f" {e['H3']:>7.4f} {e['F3']:>7.4f}"
            escribir(fila)
            guardar_csv(nombre, f"fragmento_{tam}", "H1", round(e["H1"], 6))
            guardar_csv(nombre, f"fragmento_{tam}", "H3", round(e["H3"], 6))
        escribir()


def parte_huffman(normalizados):
    """Huffman sobre cada texto normalizado."""
    escribir("=" * 80)
    escribir("3. HUFFMAN (sobre el texto normalizado)")
    escribir("   bpc = bits por caracter contando la tabla de codigos y la cabecera")
    escribir("=" * 80)
    titulo = f"{'texto':<10} {'H1':>7} {'L':>7} {'eficiencia':>10}"
    titulo = titulo + f" {'bytes':>9} {'tabla':>6} {'bpc':>7} {'ok':>4}"
    escribir(titulo)
    resultados = {}
    longitudes = {}
    for nombre in normalizados:
        texto = normalizados[nombre]
        # armamos el codigo de huffman
        frec = huffman.frecuencias(texto)
        arbol = huffman.construir_arbol(frec)
        codigos = huffman.generar_codigos(arbol)
        bits = huffman.codificar(texto, codigos)

        # empaquetamos en bytes, desempaquetamos y decodificamos para verificar
        datos = huffman.empaquetar_bits(bits)
        bits_recuperados = huffman.desempaquetar_bits(datos, len(bits))
        recuperado = huffman.decodificar(bits_recuperados, arbol)
        ok = recuperado == texto

        h1 = calcular_entropias(texto)["H1"]
        L = huffman.longitud_media(codigos, frec)
        eficiencia = h1 / L
        total_bytes = huffman.tamano_comprimido(bits, codigos)
        tabla = huffman.tamano_tabla(codigos)
        bpc = compresion.bits_por_caracter(total_bytes, len(texto))
        resultados[nombre] = bpc
        longitudes[nombre] = L

        if ok:
            si_no = "si"
        else:
            si_no = "NO"
        fila = f"{nombre:<10} {h1:>7.4f} {L:>7.4f} {eficiencia:>10.4f}"
        fila = fila + f" {total_bytes:>9} {tabla:>6} {bpc:>7.4f} {si_no:>4}"
        escribir(fila)
        guardar_csv(nombre, "huffman", "L", round(L, 6))
        guardar_csv(nombre, "huffman", "eficiencia", round(eficiencia, 6))
        guardar_csv(nombre, "huffman", "bytes", total_bytes)
        guardar_csv(nombre, "huffman", "bits_por_caracter", round(bpc, 6))
        guardar_csv(nombre, "huffman", "decodificado_ok", ok)
    escribir()
    return resultados, longitudes


def parte_compresion(originales, normalizados):
    """zlib y gzip sobre el archivo original y sobre el normalizado."""
    escribir("=" * 80)
    escribir("4. ZLIB Y GZIP (niveles 1, 6 y 9)")
    escribir("   bpc = 8 * bytes comprimidos / numero de caracteres")
    escribir("   razon = bytes sin comprimir / bytes comprimidos")
    escribir("=" * 80)
    titulo = f"{'texto':<10} {'version':<11} {'metodo':<8}"
    titulo = titulo + f" {'bytes_in':>9} {'bytes_out':>9} {'bpc':>7} {'razon':>7}"
    escribir(titulo)
    # aqui guardamos los bpc del normalizado para el resumen
    bpc_normalizado = {}
    for nombre in originales:
        bpc_normalizado[nombre] = {}
        # las dos versiones: el archivo tal cual y el normalizado
        # cada version es [etiqueta, texto, bytes]
        bytes_orig = compresion.a_bytes_original(originales[nombre])
        bytes_norm = compresion.a_bytes_normalizado(normalizados[nombre])
        versiones = []
        versiones.append(["original", originales[nombre], bytes_orig])
        versiones.append(["normalizado", normalizados[nombre], bytes_norm])
        for version in versiones:
            etiqueta = version[0]
            texto = version[1]
            datos = version[2]
            for nivel in compresion.NIVELES:
                # probamos zlib y gzip con el mismo nivel
                tam_zlib = compresion.tamano_zlib(datos, nivel)
                tam_gzip = compresion.tamano_gzip(datos, nivel)
                metodos = [["zlib", tam_zlib], ["gzip", tam_gzip]]
                for m in metodos:
                    nombre_metodo = f"{m[0]}-{nivel}"
                    tam = m[1]
                    bpc = compresion.bits_por_caracter(tam, len(texto))
                    razon = compresion.razon_compresion(len(datos), tam)
                    if etiqueta == "normalizado":
                        bpc_normalizado[nombre][nombre_metodo] = bpc
                    fila = f"{nombre:<10} {etiqueta:<11} {nombre_metodo:<8}"
                    fila = fila + f" {len(datos):>9} {tam:>9} {bpc:>7.4f} {razon:>7.3f}"
                    escribir(fila)
                    seccion = f"{etiqueta}_{nombre_metodo}"
                    guardar_csv(nombre, seccion, "bytes", tam)
                    guardar_csv(nombre, seccion, "bits_por_caracter", round(bpc, 6))
                    guardar_csv(nombre, seccion, "razon", round(razon, 6))
        escribir()
    return bpc_normalizado


def parte_resumen(normalizados, entropias, bpc_huffman, L_huffman, bpc_normalizado):
    """Comparacion rapida: entropia vs huffman vs zlib-9 en el normalizado."""
    escribir("=" * 80)
    escribir("5. RESUMEN (texto normalizado, bits por caracter)")
    escribir("=" * 80)
    titulo = f"{'texto':<10} {'H1':>7} {'H2':>7} {'H3':>7} {'F3':>7}"
    titulo = titulo + f" {'L':>7} {'huffman':>8} {'zlib-9':>7} {'gzip-9':>7}"
    escribir(titulo)
    # usamos lo que ya se calculo en las partes anteriores
    for nombre in normalizados:
        e = entropias[nombre]
        l = L_huffman[nombre]
        b = bpc_huffman[nombre]
        z = bpc_normalizado[nombre]["zlib-9"]
        g = bpc_normalizado[nombre]["gzip-9"]
        fila = f"{nombre:<10} {e['H1']:>7.4f} {e['H2']:>7.4f} {e['H3']:>7.4f} {e['F3']:>7.4f}"
        fila = fila + f" {l:>7.4f} {b:>8.4f} {z:>7.4f} {g:>7.4f}"
        escribir(fila)
    escribir()


def main():
    # 1. bajamos los libros y generamos los otros textos
    preparar_corpus()
    originales = cargar_textos()

    # 2. normalizamos todo menos el aleatorio (ese ya esta en el alfabeto,
    # y normalizar juntaria los espacios dobles y dañaria la equiprobabilidad)
    normalizados = {}
    for nombre in originales:
        if nombre == "aleatorio":
            normalizados[nombre] = originales[nombre]
        else:
            normalizados[nombre] = normalizar(originales[nombre])

    escribir()
    escribir("ENTROPIA Y COMPRESION DE TEXTO")
    escribir()
    escribir(f"{'texto':<10} {'caracteres originales':>22} {'simbolos normalizados':>22}")
    for nombre in originales:
        escribir(f"{nombre:<10} {len(originales[nombre]):>22} {len(normalizados[nombre]):>22}")
    escribir()

    entropias = parte_entropias(normalizados)
    parte_fragmentos(normalizados)
    bpc_huffman, L_huffman = parte_huffman(normalizados)
    bpc_normalizado = parte_compresion(originales, normalizados)
    parte_resumen(normalizados, entropias, bpc_huffman, L_huffman, bpc_normalizado)

    # guardamos los resultados en archivos
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)
    ruta_txt = os.path.join(CARPETA_RESULTADOS, "resultados.txt")
    ruta_csv = os.path.join(CARPETA_RESULTADOS, "resultados.csv")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["texto", "seccion", "medida", "valor"])
        for fila in filas_csv:
            escritor.writerow(fila)
    print("resultados guardados en resultados/resultados.txt y resultados/resultados.csv")


main()
