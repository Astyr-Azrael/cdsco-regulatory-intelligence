"""Drug/product comparison keys that retain strength and dosage-form signals."""

from __future__ import annotations

import re
import unicodedata


FORM_TERMS = (
    "tablet", "tablets", "capsule", "capsules", "injection", "syrup",
    "suspension", "solution", "cream", "ointment", "gel", "drops", "bolus",
)


def normalize_drug_name(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold()
    text = text.replace("&", " and ")
    text = re.sub(r"\bi\s*\.?\s*p\s*\.?\b", " ip ", text)
    text = re.sub(r"\bu\s*\.?\s*s\s*\.?\s*p\s*\.?\b", " usp ", text)
    text = re.sub(r"(?<=\d)\s+(?=(?:mg|mcg|g|ml|%|iu)\b)", "", text)
    # Preserve decimal points and concentration denominators in identity keys.
    text = re.sub(r"(?<!\d)\.|\.(?!\d)", " ", text)
    text = re.sub(r"[^a-z0-9%./]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_strengths(value: str) -> tuple[str, ...]:
    text = unicodedata.normalize("NFKC", value or "").casefold()
    strengths = re.findall(r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|%|iu)(?:\s*/\s*\d+(?:\.\d+)?\s*ml)?\b", text)
    return tuple(sorted({re.sub(r"\s+", "", item) for item in strengths}))


def extract_dosage_forms(value: str) -> tuple[str, ...]:
    tokens = set(re.findall(r"[a-z]+", unicodedata.normalize("NFKC", value or "").casefold()))
    return tuple(term for term in FORM_TERMS if term in tokens)


def drug_parts(value: str) -> dict[str, object]:
    return {
        "display_name": " ".join(unicodedata.normalize("NFKC", value or "").split()),
        "normalized_name": normalize_drug_name(value),
        "strengths": extract_strengths(value),
        "dosage_forms": extract_dosage_forms(value),
    }


def compatible_products(left: dict, right: dict) -> bool:
    """Reject numeric, strength, form and explicitly conflicting standard signals."""
    a, b = left["normalized_name"], right["normalized_name"]
    if re.findall(r"\d+(?:\.\d+)?", a) != re.findall(r"\d+(?:\.\d+)?", b):
        return False
    standards = lambda s: set(s.split()) & {"ip", "bp", "usp", "ep"}
    if standards(a) and standards(b) and standards(a) != standards(b):
        return False
    if set(left["strengths"]) != set(right["strengths"]):
        return False
    forms = lambda p: {s.removesuffix("s") for s in p["dosage_forms"]}
    return not forms(left) or not forms(right) or bool(forms(left) & forms(right))
