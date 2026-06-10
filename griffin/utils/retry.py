from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(fn: Callable[[], T], attempts: int = 3, base_delay: float = 0.25) -> T:
    last_error: Exception | None = None
    for idx in range(attempts):
        try:
            return fn()
        except Exception as exc:  # pragma: no cover - exercised by live integrations
            last_error = exc
            if idx < attempts - 1:
                time.sleep(base_delay * (2**idx))
    assert last_error is not None
    raise last_error
