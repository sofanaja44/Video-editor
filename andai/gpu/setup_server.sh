#!/usr/bin/env bash
# Prepare a GPU server (target: RTX 5090, Ubuntu 22.04/24.04) for ANDAI Blender rendering,
# then run the render benchmark. Usage, from the repo root:  bash andai/gpu/setup_server.sh
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-5.2.3}"
BLENDER_SERIES="${BLENDER_VERSION%.*}"
BLENDER_ROOT="${BLENDER_ROOT:-$HOME/blender}"
BLENDER_DIR="$BLENDER_ROOT/blender-${BLENDER_VERSION}-linux-x64"
# optional: a tarball already on this machine (copied from the asset store by gpu.sh) used instead of downloading
BLENDER_TARBALL="${BLENDER_TARBALL:-}"
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
  mkdir -p "$BLENDER_ROOT"
  if [ -n "$BLENDER_TARBALL" ] && [ -f "$BLENDER_TARBALL" ]; then
    echo "memakai cadangan lokal: $BLENDER_TARBALL"
    tar -xJf "$BLENDER_TARBALL" -C "$BLENDER_ROOT"
  else
    curl -fsSL "https://download.blender.org/release/Blender${BLENDER_SERIES}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
      | tar -xJ -C "$BLENDER_ROOT"
  fi
fi
mkdir -p "$HOME/.local/bin"
ln -sf "$BLENDER_DIR/blender" "$HOME/.local/bin/blender"
"$BLENDER_DIR/blender" --version | head -1

if [ "${SKIP_BENCH:-0}" = "1" ]; then
  echo "Selesai (uji render dilewati). Blender: $BLENDER_DIR/blender"
  exit 0
fi

echo "== 4. Uji render (adegan Si Kamu, 1080x1920)"
mkdir -p "$OUT"
SCENE="$REPO/andai/scene3d/prototipe/blender_scene.py"
# timeout: EEVEE has no GPU context in containers without NVIDIA graphics libs and then crawls on the CPU.
run() { timeout "${RENDER_TIMEOUT:-120}" "$BLENDER_DIR/blender" -b --python "$SCENE" -- "$@" 2>&1 | grep -E "render [0-9]|devices:|Error" || echo "(gagal atau melewati batas waktu: $*)"; }
{
  date
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || echo "tanpa GPU"
  if [ "${SKIP_GPU_CHECK:-0}" = "1" ]; then
    run CYCLES "$OUT/cycles_cpu.jpg" 4 CPU
  else
    [ "${TEST_EEVEE:-0}" = "1" ] && run BLENDER_EEVEE "$OUT/eevee.jpg" 0   # off by default: needs NVIDIA graphics libs
    run CYCLES "$OUT/cycles_gpu_16.jpg" 16 GPU
    run CYCLES "$OUT/cycles_gpu_64.jpg" 64 GPU
    echo "per frame, 64 sampel + denoise GPU (frame ke-2 dst. = kecepatan sebenarnya):"
    "$BLENDER_DIR/blender" -b --python "$REPO/andai/gpu/bench_frames.py" -- CYCLES "$OUT/bench.jpg" 64 GPU 4 2>&1 | grep -E "^frame " || true
  fi
} | tee "$OUT/hasil_uji.txt"
echo "Selesai. Hasil: $OUT/hasil_uji.txt dan gambar *.jpg di folder yang sama."
