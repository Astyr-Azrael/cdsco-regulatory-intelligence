import re


def normalize_manufacturer(value: str) -> str:
    text = value.strip()
    text = re.sub(r"^M/s\.?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bPvt\.?", "Private", text, flags=re.IGNORECASE)
    text = re.sub(r"\bLtd\.?", "Limited", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip(" ,.")
