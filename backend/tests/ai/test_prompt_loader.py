"""Tests de US-010: sistema de prompts versionados."""

from pathlib import Path

import pytest

from app.ai.prompts.loader import (
    PromptLoader,
    PromptNotFoundError,
    PromptVariableError,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "prompts"


@pytest.fixture
def loader() -> PromptLoader:
    return PromptLoader(base_path=FIXTURES_DIR)


def test_carga_y_renderiza_con_variables(loader: PromptLoader) -> None:
    """CA-1: el prompt se carga y renderiza con variables."""
    resultado = loader.render("saludo", nombre="Jaziel", app="Koach")

    assert resultado.strip() == "Hola Jaziel, bienvenido a Koach."


def test_variable_faltante_lanza_error_claro(loader: PromptLoader) -> None:
    """CA-2: variable faltante lanza error claro (no falla silenciosamente)."""
    with pytest.raises(PromptVariableError, match="app"):
        loader.render("saludo", nombre="Jaziel")


def test_prompt_inexistente_lanza_error_claro(loader: PromptLoader) -> None:
    with pytest.raises(PromptNotFoundError, match="no_existe"):
        loader.render("no_existe", nombre="Jaziel", app="Koach")


def test_metadata_se_carga_correctamente(loader: PromptLoader) -> None:
    template = loader.load("saludo")

    assert template.name == "saludo"
    assert template.version == "1.0.0"
    assert template.variables == ["nombre", "app"]


def test_cache_evita_releer_el_archivo_si_no_cambio(
    loader: PromptLoader, tmp_path: Path
) -> None:
    """CA-3: el YAML se puede recargar sin reiniciar el proceso (dev)."""
    prompt_path = tmp_path / "dinamico.yaml"
    prompt_path.write_text(
        "name: dinamico\nversion: \"1.0.0\"\ndescription: prueba\n"
        "variables:\n  - texto\ncontent: |\n  {{ texto }}\n",
        encoding="utf-8",
    )
    loader_dinamico = PromptLoader(base_path=tmp_path)

    primero = loader_dinamico.render("dinamico", texto="v1")
    assert primero.strip() == "v1"

    prompt_path.write_text(
        "name: dinamico\nversion: \"1.0.1\"\ndescription: prueba\n"
        "variables:\n  - texto\ncontent: |\n  {{ texto }} actualizado\n",
        encoding="utf-8",
    )
    segundo = loader_dinamico.render("dinamico", texto="v2")
    assert segundo.strip() == "v2 actualizado"
