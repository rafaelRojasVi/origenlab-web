#!/usr/bin/env python3
"""Smoke test: download MiniLM, encode on GPU, print shape/device."""
from __future__ import annotations

import sys

# This is a runnable script, not a pytest test module.
# Prevent pytest from collecting it (especially when ML deps aren't installed).
__test__ = False

try:
    import torch  # type: ignore
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    SentenceTransformer = None  # type: ignore


def main() -> None:
    if torch is None or SentenceTransformer is None:
        print("ML deps missing (torch/sentence-transformers). Run: uv sync --group ml", file=sys.stderr)
        sys.exit(2)
    print("torch:", torch.__version__)
    print("cuda:", torch.cuda.is_available())
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device:", device)

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)

    texts = [
        "Invoice from supplier for lab equipment",
        "Meeting about shipping and logistics",
        "Question about payment status",
    ]

    embeddings = model.encode(texts, convert_to_tensor=True)
    print("shape:", tuple(embeddings.shape))
    print("dtype:", embeddings.dtype)
    print("device:", embeddings.device)

    if device == "cuda" and embeddings.device.type != "cuda":
        print("WARNING: expected GPU tensors", file=sys.stderr)
        sys.exit(1)
    print("OK: embedding smoke test passed")


if __name__ == "__main__":
    main()
