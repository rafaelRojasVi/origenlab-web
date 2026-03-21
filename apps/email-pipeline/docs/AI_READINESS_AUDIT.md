# Local AI / model development readiness audit

> **Not project documentation.** This is a **one-machine environment snapshot** (hardware, drivers, installed tools). It does **not** update when the repo or your laptop changes. For **what the codebase implements**, see [AI_ML_IMPLEMENTED_SUMMARY.md](AI_ML_IMPLEMENTED_SUMMARY.md).

**Date:** 2026-03-14  
**Machine:** Windows + WSL2 Ubuntu (read-only checks; no uninstalls.)

---

## 1. Concise summary

| Area | Verdict |
|------|--------|
| **Hardware** | Strong: **Ryzen 7 9700X**, **~62 GB RAM**, **RTX 5080 (~16 GB VRAM)**. NVIDIA driver **working**; `nvidia-smi` OK on host and inside GPU Docker container. |
| **Windows dev** | **Python 3.11 / 3.12 / 3.13**, **Git**, **curl** present. Good baseline. |
| **WSL Ubuntu** | **24.04**, **Python 3.12**, **gcc**, **uv**, **Docker** client; **~1 TB** Linux disk with plenty free; **~30 GiB RAM** visible in WSL (typical WSL2 cap). |
| **Gaps** | **PyTorch not installed** in WSL system Python; **no `nvcc`** (CUDA toolkit not in WSL PATH); **FAISS / sentence-transformers** not installed; **Ollama** not in PATH. |
| **Main AI environment** | **Prefer WSL Ubuntu** for PyTorch/CUDA/Linux ML stack and Docker; use **Windows** for IDEs that need native GPU apps or when a tool is Windows-only. |

---

## 2. What is already correctly set up

### Windows host

- **OS:** Windows 11 **25H2** (build **26200**).
- **CPU:** **AMD Ryzen 7 9700X** (8-core).
- **RAM:** **~61.5 GB** total.
- **GPU:** **NVIDIA GeForce RTX 5080**; iGPU **AMD Radeon** also listed.
- **NVIDIA:** Driver reporting **576.88**; **CUDA 12.9** in SMI; **~16 GB VRAM** (16303 MiB total).
- **WSL:** **WSL 2**; default distro **Ubuntu** (Running); **docker-desktop** distro also Running.
- **Python (Windows):** **3.13** (default via `py`), **3.12**, **3.11** installed.
- **Tools:** **Git 2.45.1**, **curl** (System32).

### Ubuntu / WSL

- **Distro:** **Ubuntu 24.04.2 LTS** (noble).
- **Kernel:** **6.6.87.2-microsoft-standard-WSL2**.
- **Disk:** Root **~1007 GB**, **~946 GB free** on `/`; **C:** **~1.2 TB free** on `/mnt/c`.
- **RAM in WSL:** **30 GiB** total (WSL2 often limits to half host RAM unless `.wslconfig` changes).
- **GPU in WSL:** **`nvidia-smi`** works from WSL (same driver stack).
- **Python:** **3.12.3** (`/usr/bin/python3`).
- **uv:** **0.10.10** installed.
- **gcc:** **13.3** (build-essential-style toolchain available).
- **Docker:** **28.3.2** (Docker Desktop integration); **`docker run --gpus all ... nvidia-smi`** succeeded (GPU visible in container).

---

## 3. What is missing or broken

| Item | Status |
|------|--------|
| **PyTorch (WSL)** | **Not installed** in default `python3` → `ModuleNotFoundError: torch`. |
| **CUDA toolkit (`nvcc`) in WSL** | **Not found** — optional for many workflows (PyTorch wheels bundle runtime). |
| **FAISS** | Not installed (system Python). |
| **sentence-transformers** | Not installed. |
| **Ollama** | **Not in PATH** (WSL); not verified on Windows PATH in this audit. |
| **WSL RAM cap** | **30 GiB** vs **~62 GB** host — not “broken,” but may limit large training if not raised in `.wslconfig`. |

Nothing observed as **broken** (drivers, WSL, Docker GPU path look fine).

---

## 4. Suitability of this machine

| Workload | Fit | Notes |
|----------|-----|--------|
| **Local LLM inference** | **Excellent** | 16 GB VRAM fits many 7B–8B quants and some 13B with quantization; **Ollama** or **llama.cpp** / **vLLM** are good next steps. |
| **PyTorch training / fine-tuning** | **Very good** | RTX 5080 + 62 GB RAM; in WSL use **CUDA-enabled PyTorch**; for heavy jobs consider raising WSL memory in `.wslconfig`. |
| **Embeddings / NLP pipelines** | **Very good** | CPU RAM ample; GPU accelerates **sentence-transformers** / small models; install stack in a **venv** or **uv** project. |
| **Stable Diffusion / image models** | **Very good** | 16 GB VRAM is workable for SD 1.5/SDXL with attention tweaks; SD3/flux depends on model size and optimization. |

---

## 5. Windows vs WSL — main AI environment

**Recommendation: make WSL Ubuntu your primary environment** for:

- PyTorch, JAX (if needed), Linux-native ML libs  
- **Docker + GPU** (already validated)  
- Reproducible **uv/venv** projects  

**Keep Windows for:**

- Native apps (some SD UIs, games, Office)  
- **Py Launcher** multi-version Python if you prefer GUI IDEs on Windows  
- Copying PSTs / files from Explorer  

Use **one** canonical CUDA ML stack per project (WSL venv + PyTorch CUDA wheel) to avoid duplicate installs.

---

## 6. Ordered setup plan (missing pieces only)

Do these **in order**; confirm each step before the next if you want zero surprises.

1. **(Optional) WSL memory** — If you need **>30 GiB** in WSL: create/edit **`%UserProfile%\.wslconfig`**, set `memory=48GB` (or similar), then `wsl --shutdown`. *Ask before changing.*  
2. **PyTorch in WSL** — In a **dedicated venv** (e.g. `uv venv && uv pip install torch --index-url https://download.pytorch.org/whl/cu124` or whatever matches your CUDA — check [pytorch.org](https://pytorch.org) for RTX 50xx). *Install only when you approve.*  
3. **Embeddings stack** — Same venv: `sentence-transformers`, and optionally `faiss-cpu` or `faiss-gpu` depending on need.  
4. **Ollama** — Install on **Windows** (simplest GPU path) or Linux; then use from WSL via `localhost` if needed. *Ask before install.*  
5. **CUDA toolkit (`nvcc`)** — Only if you compile custom CUDA extensions; otherwise **skip**; PyTorch wheels usually enough.  
6. **Docker GPU** — Already working; ensure **WSL2 backend** + **GPU** enabled in Docker Desktop for future compose runs.

---

## 7. Benefit checklist

| Capability | Benefit on this PC |
|------------|--------------------|
| **Ollama** | Quick local LLM inference; matches strong GPU. |
| **PyTorch in WSL** | Primary stack for training/fine-tuning and CUDA. |
| **CUDA toolkit** | Low priority unless building from source. |
| **Docker + GPU** | Already usable; good for reproducible training/inference images. |
| **FAISS + sentence-transformers** | Strong for embeddings/RAG; install per project. |

---

## 8. Commands reference (what was run)

**Windows (PowerShell):** OS build, `Win32_Processor`, `Win32_ComputerSystem` (RAM), `Win32_VideoController`, `where python`, `py -0p`, `git --version`, `curl`.  

**Host / WSL:** `nvidia-smi`, `wsl --status`, `wsl -l -v`.  

**WSL:** `uname -a`, `lsb_release -a`, `df -h`, `free -h`, `python3 --version`, `uv --version`, `gcc --version`, `nvcc` (absent), PyTorch import test (failed — not installed), FAISS/sentence-transformers (not installed).  

**Docker:** `docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi` — **pulled image** once; confirms GPU in containers.

---

*End of report.*
