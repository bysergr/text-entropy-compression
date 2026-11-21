# normalizacion del texto: dejamos solo las 27 letras y el espacio

ALFABETO = "abcdefghijklmnñopqrstuvwxyz "

# tabla para quitar tildes y dieresis (la ñ NO se toca)
TILDES = {
    "á": "a", "à": "a", "â": "a", "ä": "a", "ã": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "ö": "o", "õ": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ý": "y", "ÿ": "y",
    "ç": "c",
}

# ligaduras que se cambian por dos letras (p.ej. manœuvre -> manoeuvre)
LIGADURAS = {"œ": "oe", "æ": "ae", "ß": "ss"}


def normalizar(texto):
    """Pasa a minusculas, quita tildes y deja solo letras y espacios."""
    # todo a minusculas (la Ñ queda como ñ)
    texto = texto.lower()

    # cambiamos cada caracter: tildes fuera y lo raro se vuelve espacio
    letras = []
    for c in texto:
        # las ligaduras se vuelven dos letras
        if c in LIGADURAS:
            letras.append(LIGADURAS[c])
            continue
        if c in TILDES:
            c = TILDES[c]
        if c in ALFABETO:
            letras.append(c)
        else:
            letras.append(" ")
    texto = "".join(letras)

    # dejamos un solo espacio entre palabras y quitamos los de los bordes
    palabras = texto.split()
    return " ".join(palabras)
