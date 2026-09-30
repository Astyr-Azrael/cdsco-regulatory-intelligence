import re


def normalize_batch(value: str) -> str:
    return re.sub(r"\s+", "", value.strip()).upper()
