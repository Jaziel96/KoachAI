"""Tests del split de mensajes largos (US-017, RF-5 / CA-4)."""

from app.adapters.whatsapp.text_splitter import MAX_LENGTH, split_text


def test_mensaje_corto_no_se_divide() -> None:
    assert split_text("hola") == ["hola"]


def test_texto_vacio_o_en_blanco_no_genera_partes() -> None:
    assert split_text("") == []
    assert split_text("  \n ") == []


def test_exactamente_en_el_limite_no_se_divide() -> None:
    texto = "a" * MAX_LENGTH
    assert split_text(texto) == [texto]


def test_ca4_mensaje_largo_se_divide_sin_cortar_palabras() -> None:
    palabras = [f"palabra{i}" for i in range(2000)]
    texto = " ".join(palabras)
    assert len(texto) > MAX_LENGTH * 2

    partes = split_text(texto)

    assert len(partes) >= 3
    assert all(0 < len(p) <= MAX_LENGTH for p in partes)
    assert " ".join(partes).split() == palabras


def test_prefiere_cortar_en_salto_de_linea() -> None:
    parrafo_1 = "a" * 3000
    parrafo_2 = "b" * 3000
    assert split_text(f"{parrafo_1}\n{parrafo_2}") == [parrafo_1, parrafo_2]


def test_palabra_mas_larga_que_el_limite_se_parte_a_la_fuerza() -> None:
    partes = split_text("x" * (MAX_LENGTH + 10))
    assert [len(p) for p in partes] == [MAX_LENGTH, 10]
