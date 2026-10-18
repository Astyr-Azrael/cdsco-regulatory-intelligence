"""Conservative manufacturer normalization for candidate generation.

Raw CDSCO values are never changed.  These functions create comparison keys and
display suggestions only; they do not establish legal identity.
"""

from __future__ import annotations

import re
import unicodedata


CORPORATE_REPLACEMENTS = (
    (r"\bm\s*/\s*s\.?\b", " "),
    (r"\(\s*p\s*\)", " private "),
    (r"\bpvt\.?\b", " private "),
    (r"\bpte\.?\b", " private "),
    (r"\bltd\.?\b", " limited "),
    (r"\bco\.?\b", " company "),
)

ADDRESS_REPLACEMENTS = (
    (r"\bdistt?\.?\b", " district "),
    (r"\bindl\.?\b", " industrial "),
    (r"\bopp\.?\b", " opposite "),
    (r"\brd\.?\b", " road "),
    (r"\bvill\.?\b", " village "),
    (r"\bpo\.?\b", " post office "),
)

ADDRESS_MARKERS = re.compile(
    r"(?:,|\s+-\s+|\bat\b|\bplot\b|\bkhasra\b|\bsurvey\b|\bvillage\b|\bvill\.?\b|\bunit[- ]?\d|\bno\.?\s*\d)",
    re.IGNORECASE,
)


def _basic(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold().replace("&", " and ")
    for pattern, replacement in CORPORATE_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_manufacturer_mention(value: str) -> tuple[str, str | None]:
    """Split an observed combined name/address cell at the first strong marker."""
    cleaned = " ".join(unicodedata.normalize("NFKC", value or "").split()).strip(" ,.;")
    if not cleaned:
        return "", None
    marker = ADDRESS_MARKERS.search(cleaned)
    if not marker or marker.start() < 3:
        return cleaned, None
    name = cleaned[: marker.start()].strip(" ,.-")
    address = cleaned[marker.start() :].strip(" ,.-")
    return (name or cleaned), (address or None)


def normalize_manufacturer(value: str) -> str:
    """Return a stable comparison key while preserving corporate meaning."""
    name, _ = split_manufacturer_mention(value)
    return _basic(name)


def normalize_address(value: str | None) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold().replace("&", " and ")
    for pattern, replacement in ADDRESS_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:india|pin|pincode)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def manufacturer_parts(value: str, explicit_address: str | None = None) -> dict[str, str | None]:
    name, embedded_address = split_manufacturer_mention(value)
    address = explicit_address or embedded_address
    return {
        "display_name": name,
        "normalized_name": normalize_manufacturer(name),
        "address": address,
        "normalized_address": normalize_address(address) or None,
    }
