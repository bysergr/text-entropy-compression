# calculo de entropias de un texto (por letra, condicional y redundancia)
import math

# entropia maxima con 28 simbolos (27 letras + espacio)
HMAX = math.log2(28)


def contar_bloques(texto, n):
    """Cuenta cuantas veces aparece cada bloque de n simbolos."""
    conteo = {}
    # ventana deslizante: tomamos texto[i:i+n] para cada posicion
    for i in range(len(texto) - n + 1):
        bloque = texto[i:i + n]
        if bloque in conteo:
            conteo[bloque] = conteo[bloque] + 1
        else:
            conteo[bloque] = 1
    return conteo


def entropia_conjunta(texto, n):
    """Entropia conjunta H(X1..Xn) en bits."""
    conteo = contar_bloques(texto, n)
    # total de bloques que salieron
    total = 0
    for bloque in conteo:
        total = total + conteo[bloque]
    if total == 0:
        return 0.0
    # sumamos -p*log2(p) para cada bloque
    h = 0.0
    for bloque in conteo:
        p = conteo[bloque] / total
        h = h - p * math.log2(p)
    return h


def calcular_entropias(texto):
    """Calcula H1, H2, H3, F2, F3, R1 y R3 de un texto."""
    # primero las entropias conjuntas de bloques de 1, 2 y 3
    h_1 = entropia_conjunta(texto, 1)
    h_2 = entropia_conjunta(texto, 2)
    h_3 = entropia_conjunta(texto, 3)

    resultado = {}
    # entropia por letra usando bloques
    # para n=1 la entropia por letra es la misma conjunta
    resultado["H1"] = h_1
    resultado["H2"] = h_2 / 2
    resultado["H3"] = h_3 / 3
    # entropia condicional (lo que aporta la letra nueva)
    resultado["F2"] = h_2 - h_1
    resultado["F3"] = h_3 - h_2
    # redundancia comparando con la entropia maxima
    resultado["R1"] = 1 - resultado["H1"] / HMAX
    resultado["R3"] = 1 - resultado["H3"] / HMAX
    return resultado
