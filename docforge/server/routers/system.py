"""System router — health, themes, providers."""

from __future__ import annotations

from fastapi import APIRouter

from docforge.templates.engine import list_themes

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": _docforge_version()}


@router.get("/themes")
async def themes() -> list[dict]:
    return [
        {
            "id": t.get("id"),
            "version": t.get("version"),
            "author": t.get("author"),
            "supports_cover": t.get("manifest", {}).get("supports_cover", False),
            "supports_sidebars": t.get("manifest", {}).get("supports_sidebars", False),
        }
        for t in list_themes()
    ]


@router.get("/providers")
async def providers() -> dict:
    image_providers = []
    for name in ["wikimedia", "unsplash", "pexels"]:
        image_providers.append({"id": name, "available": True, "requires_key": name != "wikimedia"})

    ai_providers = []
    try:
        import openai  # noqa: F401

        ai_providers.append({"id": "openai", "available": True})
    except ImportError:
        ai_providers.append({"id": "openai", "available": False, "reason": "openai not installed"})

    return {"ai": ai_providers, "images": image_providers}


def _docforge_version() -> str:
    try:
        from importlib.metadata import version

        return version("docforge")
    except Exception:
        return "dev"
