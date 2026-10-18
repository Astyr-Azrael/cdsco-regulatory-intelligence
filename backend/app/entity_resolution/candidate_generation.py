from __future__ import annotations

from collections import defaultdict
from itertools import combinations


STOPWORDS = {"private", "limited", "company", "pharmaceuticals", "pharma", "laboratories", "labs", "the", "and"}


def candidate_keys(name: str, location: str | None = None) -> set[str]:
    tokens = [token for token in name.casefold().split() if len(token) > 2 and token not in STOPWORDS]
    keys = {f"prefix:{name[:8]}"} if name else set()
    keys.update(f"token:{token}" for token in tokens[:5])
    if location:
        location_tokens = [token for token in location.casefold().split() if len(token) > 3]
        keys.update(f"location:{token}" for token in location_tokens[-4:])
    return keys


def generate_candidate_pairs(items: list[dict], *, max_block_size: int = 80) -> list[tuple[dict, dict]]:
    """Block mentions by name/location tokens instead of comparing every pair."""
    blocks: dict[str, list[int]] = defaultdict(list)
    for index, item in enumerate(items):
        for key in candidate_keys(item["normalized_name"], item.get("normalized_address")):
            blocks[key].append(index)
    pairs: set[tuple[int, int]] = set()
    for members in blocks.values():
        unique = sorted(set(members))
        if 1 < len(unique) <= max_block_size:
            pairs.update(combinations(unique, 2))
    return [(items[left], items[right]) for left, right in sorted(pairs)]
