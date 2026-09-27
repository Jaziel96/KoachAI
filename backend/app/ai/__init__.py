"""Capa de abstracción de IA, agnóstica de proveedor (ADR-002, ADR-007).

Ningún módulo fuera de `app/ai/` debe importar SDKs de proveedores
(anthropic, google.generativeai, etc.) directamente.
"""
