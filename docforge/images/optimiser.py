"""Image optimiser — resize, crop, sRGB normalisation, JPEG compression via Pillow."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageCms

from docforge.logging.setup import get_logger

logger = get_logger(__name__)

_SRGB_PROFILE = ImageCms.createProfile("sRGB")
_DEFAULT_QUALITY = 85


def optimise(
    source: Path,
    target: Path,
    max_width: int = 1920,
    max_height: int = 1080,
    quality: int = _DEFAULT_QUALITY,
) -> Path:
    """Optimise an image: resize, convert to sRGB, compress as JPEG.

    Attribution metadata (EXIF 0x013b Artist) is preserved if present.
    """
    target.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as raw:
        img: Image.Image = raw
        exif = _extract_exif(img)
        img = _to_srgb(img)
        img = _resize(img, max_width, max_height)
        img = img.convert("RGB")

        save_kwargs: dict = {"format": "JPEG", "quality": quality, "optimize": True}
        if exif:
            save_kwargs["exif"] = exif

        img.save(target, **save_kwargs)

    logger.debug("image_optimised", source=str(source), target=str(target))
    return target


def _resize(img: Image.Image, max_width: int, max_height: int) -> Image.Image:
    w, h = img.size
    if w <= max_width and h <= max_height:
        return img
    ratio = min(max_width / w, max_height / h)
    new_size = (int(w * ratio), int(h * ratio))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def _to_srgb(img: Image.Image) -> Image.Image:
    try:
        icc = img.info.get("icc_profile")
        if icc:
            src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            result = ImageCms.profileToProfile(img, src_profile, _SRGB_PROFILE, outputMode="RGB")
            if isinstance(result, Image.Image):
                return result
    except Exception:
        pass
    return img


def _extract_exif(img: Image.Image) -> bytes | None:
    try:
        return img.info.get("exif")
    except Exception:
        return None
