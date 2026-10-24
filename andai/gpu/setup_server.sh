#!/usr/bin/env bash
# Prepare a GPU server (target: RTX 5090, Ubuntu 22.04/24.04) for ANDAI Blender rendering,
# then run the render benchmark. Usage, from the repo root:  bash andai/gpu/setup_server.sh
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-5.2.3}"
BLENDER_SERIES="${BLENDER_VERSION%.*}"
BLENDER_DIR="$HOME/blender/blender-${BLENDER_VERSION}-linux-x64"
SUDO=""; [ "$(id -u)" != "0" ] && SUDO="sudo"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$REPO/andai/gpu/hasil"

echo "== 1. GPU"
if [ "${SKIP_GPU_CHECK:-0}" != "1" ]; then
  if ! command -v nvidia-smi >/dev/null || ! nvidia-smi >/dev/null 2>&1; then
    echo "Driver NVIDIA belum aktif. RTX 5090 butuh driver versi 570 ke atas (varian 'open'), mis.:"
    echo "  sudo apt update && sudo apt install -y nvidia-driver-570-open && sudo reboot"
    exit 1
  fi
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
fi

echo "== 2. Paket sistem"
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq ffmpeg tmux git curl xz-utils python3-venv \
  libegl1 libgl1 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 >/dev/null

echo "== 3. Blender $BLENDER_VERSION"
if [ ! -x "$BLENDER_DIR/blender" ]; then
  mkdir -p "$HOME/blender"
  curl -fsSL "https://download.blender.org/release/Blender${BLENDER_SERIES}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
    | tar -xJ -C "$HOME/blender"
fi
mkdir -p "$HOME/.local/bin"
ln -sf "$BLENDER_DIR/blender" "$HOME/.local/bin/blender"
"$BLENDER_DIR/blender" --version | head -1

echo "== 4. Uji render (adegan Si Kamu, 1080x1920)"
mkdir -p "$OUT"
SCENE="$REPO/andai/scene3d/prototipe/blender_scene.py"
run() { "$BLENDER_DIR/blender" -b --python "$SCENE" -- "$@" 2>&1 | grep -E "render [0-9]|devices:|Error" || true; }
{
  date
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || echo "tanpa GPU"
  if [ "${SKIP_GPU_CHECK:-0}" = "1" ]; then
    run CYCLES "$OUT/cycles_cpu.jpg" 4 CPU
  else
    run BLENDER_EEVEE "$OUT/eevee.jpg" 0
    run CYCLES "$OUT/cycles_gpu_16.jpg" 16 GPU
    run CYCLES "$OUT/cycles_gpu_64.jpg" 64 GPU
  fi
} | tee "$OUT/hasil_uji.txt"
echo "Selesai. Hasil: $OUT/hasil_uji.txt dan gambar *.jpg di folder yang sama."
