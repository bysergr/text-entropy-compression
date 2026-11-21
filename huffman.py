# codificacion de Huffman hecha a mano
import heapq
import math


def frecuencias(texto):
    """Cuenta cuantas veces aparece cada letra."""
    frec = {}
    for letra in texto:
        if letra in frec:
            frec[letra] = frec[letra] + 1
        else:
            frec[letra] = 1
    return frec


def construir_arbol(frec):
    """Arma el arbol de Huffman con un heap."""
    heap = []
    contador = 0
    # metemos cada letra como una hoja
    # el contador sirve para desempatar, si no heapq intenta comparar los nodos
    for letra in sorted(frec):
        heapq.heappush(heap, (frec[letra], contador, letra))
        contador = contador + 1

    # si solo hay una letra el arbol es la hoja sola
    if len(heap) == 1:
        return heap[0][2]

    # juntamos los dos nodos con menor frecuencia hasta que quede uno
    while len(heap) > 1:
        # c1 y c2 son los contadores de desempate, aca no los usamos
        f1, c1, nodo1 = heapq.heappop(heap)
        f2, c2, nodo2 = heapq.heappop(heap)
        nuevo = [nodo1, nodo2]
        heapq.heappush(heap, (f1 + f2, contador, nuevo))
        contador = contador + 1

    return heap[0][2]


def recorrer(nodo, camino, codigos):
    """Baja por el arbol guardando el camino de cada hoja."""
    # si es un string es una hoja (una letra)
    if isinstance(nodo, str):
        codigos[nodo] = camino
        return
    # izquierda es 0 y derecha es 1
    recorrer(nodo[0], camino + "0", codigos)
    recorrer(nodo[1], camino + "1", codigos)


def generar_codigos(arbol):
    """Devuelve un diccionario letra -> codigo de bits."""
    codigos = {}
    # caso especial: un solo simbolo, le ponemos "0"
    if isinstance(arbol, str):
        codigos[arbol] = "0"
        return codigos
    recorrer(arbol, "", codigos)
    return codigos


def codificar(texto, codigos):
    """Pasa el texto a un string de 0s y 1s."""
    partes = []
    for letra in texto:
        partes.append(codigos[letra])
    return "".join(partes)


def empaquetar_bits(bits):
    """Mete los bits de 8 en 8 en bytes de verdad."""
    # rellenamos con ceros al final para completar el ultimo byte
    sobran = len(bits) % 8
    if sobran != 0:
        bits = bits + "0" * (8 - sobran)
    # bytearray es una lista de bytes a la que se le puede hacer append
    datos = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        # int(..., 2) lee el texto de 8 bits como un numero en binario (0 a 255)
        datos.append(int(byte, 2))
    return bytes(datos)


def desempaquetar_bits(datos, num_bits):
    """Saca los bits de los bytes y quita el relleno."""
    partes = []
    for byte in datos:
        # cada byte lo pasamos a 8 bits con ceros a la izquierda
        partes.append(format(byte, "08b"))
    bits = "".join(partes)
    return bits[:num_bits]


def decodificar(bits, arbol):
    """Recorre el arbol bit a bit para recuperar el texto."""
    # caso especial: un solo simbolo, cada bit es esa letra
    if isinstance(arbol, str):
        return arbol * len(bits)

    resultado = []
    nodo = arbol
    for bit in bits:
        if bit == "0":
            nodo = nodo[0]
        else:
            nodo = nodo[1]
        # si llegamos a una hoja anotamos la letra y volvemos a la raiz
        if isinstance(nodo, str):
            resultado.append(nodo)
            nodo = arbol
    return "".join(resultado)


def longitud_media(codigos, frec):
    """Calcula L = suma de p(x) * largo del codigo."""
    total = 0
    for letra in frec:
        total = total + frec[letra]
    L = 0
    for letra in frec:
        p = frec[letra] / total
        L = L + p * len(codigos[letra])
    return L


def tamano_tabla(codigos):
    """Bytes que ocuparia guardar la tabla de codigos."""
    # por cada simbolo: 1 byte la letra, 1 byte el largo y los bits del codigo
    tamano = 0
    for letra in codigos:
        largo = len(codigos[letra])
        tamano = tamano + 1 + 1 + math.ceil(largo / 8)
    return tamano


def tamano_comprimido(bits, codigos):
    """Bytes totales: los bits empaquetados, la tabla y una cabecera."""
    # cabecera: 4 bytes para guardar cuantos bits hay (asi se quita el relleno)
    # y 1 byte con el numero de simbolos de la tabla
    cabecera = 4 + 1
    return len(empaquetar_bits(bits)) + tamano_tabla(codigos) + cabecera
