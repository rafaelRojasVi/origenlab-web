"""Small helpers for consistent CLI progress bars.

Uses tqdm when available, otherwise falls back to plain iteration.
"""
from __future__ import annotations

from typing import Iterable, Iterator, TypeVar

T = TypeVar("T")

try:  # pragma: no cover - trivial import guard
    from tqdm import tqdm  # type: ignore
except Exception:  # pragma: no cover - when tqdm is not installed
    tqdm = None  # type: ignore


def iter_with_progress(
    iterable: Iterable[T],
    *,
    total: int | None = None,
    desc: str = "",
    unit: str = "items",
) -> Iterator[T]:
    """Wrap an iterable with a tqdm progress bar when available.

    - If tqdm is installed, shows a bar with total/ETA.
    - If not, just returns the original iterable unchanged.
    """
    if tqdm is None or total is not None and total <= 0:
        # Fallback: no tqdm or nothing to show
        return iter(iterable)
    return tqdm(
        iterable,
        total=total,
        desc=desc,
        unit=unit,
        dynamic_ncols=True,
        miniters=1000,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
    )

