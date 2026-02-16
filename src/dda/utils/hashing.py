from __future__ import annotations

import hashlib


def short_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
