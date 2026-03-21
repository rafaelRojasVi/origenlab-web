#!/usr/bin/env python3
"""Verify sentence-transformers and FAISS import in the active venv."""
from __future__ import annotations

import sys


def main() -> None:
    print("=== check_embeddings_stack.py ===")
    print("python_executable:", sys.executable)

    # Torch (expected for sentence-transformers GPU)
    try:
        import torch

        print("torch_version:", torch.__version__)
        print("torch_cuda_is_available:", torch.cuda.is_available())
        print("torch_cuda_device_count:", torch.cuda.device_count())
        if torch.cuda.is_available():
            print("torch_cuda_device_0_name:", torch.cuda.get_device_name(0))
            print("torch_bundled_cuda:", torch.version.cuda)
        else:
            print("torch_cuda_device_0_name:", "(n/a)")
            print("torch_bundled_cuda:", getattr(torch.version, "cuda", None))
    except ImportError as e:
        print("torch_import:", False, repr(e))
        sys.exit(1)

    try:
        import sentence_transformers

        print("sentence_transformers_import:", True)
        print("sentence_transformers_version:", getattr(sentence_transformers, "__version__", "unknown"))
    except ImportError as e:
        print("sentence_transformers_import:", False)
        print("sentence_transformers_error:", repr(e))

    try:
        import faiss

        print("faiss_import:", True)
        # faiss often has no __version__ on CPU build
        ver = getattr(faiss, "__version__", None) or getattr(faiss, "version", None) or "(no __version__)"
        print("faiss_version_or_note:", ver)
    except ImportError as e:
        print("faiss_import:", False)
        print("faiss_error:", repr(e))


if __name__ == "__main__":
    main()
