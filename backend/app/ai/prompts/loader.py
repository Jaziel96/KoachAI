"""Carga y renderizado de prompts versionados (US-010).

Los prompts viven como archivos YAML en `app/ai/prompts/system/` (nunca
hardcodeados en Python, regla no negociable #2 de CLAUDE.md). `PromptLoader`
los lee, valida sus variables y los renderiza con Jinja2.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from jinja2 import StrictUndefined, Template
from jinja2.exceptions import UndefinedError
from pydantic import BaseModel


class PromptTemplate(BaseModel):
    """Metadata y contenido de un prompt, tal como se definen en el YAML."""

    name: str
    version: str
    description: str
    variables: list[str]
    content: str


class PromptNotFoundError(Exception):
    """El prompt solicitado no existe en `base_path`."""

    def __init__(self, prompt_id: str) -> None:
        super().__init__(f"Prompt no encontrado: '{prompt_id}'")


class PromptVariableError(Exception):
    """Falta una variable requerida al renderizar un prompt."""

    def __init__(self, prompt_id: str, variables_faltantes: list[str]) -> None:
        faltantes = ", ".join(variables_faltantes)
        super().__init__(
            f"Faltan variables requeridas para el prompt '{prompt_id}': {faltantes}"
        )


class _CacheEntry(BaseModel):
    template: PromptTemplate
    mtime: float


class PromptLoader:
    """Carga prompts YAML desde disco con caché en memoria (RF-3).

    El caché se invalida automáticamente cuando cambia el mtime del archivo
    (CA-3: permite editar el YAML en dev sin reiniciar el proceso).
    """

    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path
        self._cache: dict[str, _CacheEntry] = {}

    def load(self, prompt_id: str) -> PromptTemplate:
        path = self._base_path / f"{prompt_id}.yaml"
        if not path.is_file():
            raise PromptNotFoundError(prompt_id)

        mtime = path.stat().st_mtime
        cached = self._cache.get(prompt_id)
        if cached is not None and cached.mtime == mtime:
            return cached.template

        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        template = PromptTemplate.model_validate(raw)
        self._cache[prompt_id] = _CacheEntry(template=template, mtime=mtime)
        return template

    def render(self, prompt_id: str, **kwargs: object) -> str:
        template = self.load(prompt_id)

        faltantes = [v for v in template.variables if v not in kwargs]
        if faltantes:
            raise PromptVariableError(prompt_id, faltantes)

        jinja_template = Template(template.content, undefined=StrictUndefined)
        try:
            return jinja_template.render(**kwargs)
        except UndefinedError as exc:
            raise PromptVariableError(prompt_id, [str(exc)]) from exc
