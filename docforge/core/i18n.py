"""i18n string tables for auto-generated labels (T045)."""

from __future__ import annotations

_LABELS: dict[str, dict[str, str]] = {
    "toc": {
        "en": "Table of Contents",
        "ru": "Содержание",
        "es": "Índice",
        "de": "Inhaltsverzeichnis",
        "fr": "Table des matières",
    },
    "figure": {
        "en": "Figure",
        "ru": "Рисунок",
        "es": "Figura",
        "de": "Abbildung",
        "fr": "Figure",
    },
    "table": {
        "en": "Table",
        "ru": "Таблица",
        "es": "Tabla",
        "de": "Tabelle",
        "fr": "Tableau",
    },
    "image_sources": {
        "en": "Image Sources",
        "ru": "Источники изображений",
        "es": "Fuentes de imágenes",
        "de": "Bildquellen",
        "fr": "Sources des images",
    },
    "page": {
        "en": "Page",
        "ru": "Страница",
        "es": "Página",
        "de": "Seite",
        "fr": "Page",
    },
    "appendix": {
        "en": "Appendix",
        "ru": "Приложение",
        "es": "Apéndice",
        "de": "Anhang",
        "fr": "Annexe",
    },
}


def get_label(key: str, language: str = "en") -> str:
    lang = language.lower().split("-")[0]
    return _LABELS.get(key, {}).get(lang) or _LABELS.get(key, {}).get("en") or key
