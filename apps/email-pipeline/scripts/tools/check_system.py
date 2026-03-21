#!/usr/bin/env python3
"""Lightweight system snapshot (no ML imports). Safe to run anywhere."""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys


def main() -> None:
    print("=== check_system.py ===")
    print("python_executable:", sys.executable)
    print("python_version:", sys.version.split()[0])
    print("platform:", platform.platform())
    print("machine:", platform.machine())

    for name in ("uv", "gcc", "nvidia-smi"):
        path = shutil.which(name)
        print(f"which_{name}:", path or "(not in PATH)")

    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            print("nvidia_smi_gpu_line:", out.stdout.strip().replace("\n", " | "))
        except (subprocess.TimeoutExpired, OSError) as e:
            print("nvidia_smi_error:", repr(e))


if __name__ == "__main__":
    main()
