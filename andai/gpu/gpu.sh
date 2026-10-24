#!/usr/bin/env bash
# Kendali server GPU yang boleh mati: dijalankan dari mesin yang MENYIMPAN proyek dan aset (kode, episode, hasil,
# cadangan Blender). Server GPU hanya pekerja; semuanya bisa dibangun ulang di server baru dengan dua perintah:
#   bash andai/gpu/gpu.sh kunci      # pasang kunci SSH (sekali per server, minta password server sekali)
#   bash andai/gpu/gpu.sh siapkan    # kirim kode, pasang Blender, uji kecepatan
# Perintah lain: status | kirim | jalankan "<perintah>" | ambil <folder-remote> [tujuan] | cadangan | pulihkan | snapshot | cache-blender | uji
# Variabel: REMOTE_DIR, BLENDER_ROOT, BLENDER_DARI_CADANGAN=1 (paksa cadangan lokal), SKIP_BENCH=1
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
[ -f "${GPU_ENV:-$REPO/andai/gpu/gpu.env}" ] && . "${GPU_ENV:-$REPO/andai/gpu/gpu.env}"
: "${GPU_HOST:?Isi GPU_HOST di andai/gpu/gpu.env (contoh: andai/gpu/gpu.env.example)}"
GPU_PORT="${GPU_PORT:-22}"; GPU_USER="${GPU_USER:-ubuntu}"; GPU_KEY="${GPU_KEY:-$HOME/.ssh/andai_gpu}"
REMOTE_DIR="${REMOTE_DIR:-Video-editor}"; ASET="${ANDAI_ASET:-$HOME/andai-aset}"
BLENDER_ROOT="${BLENDER_ROOT:-\$HOME/blender}"   # on the GPU server (kept unexpanded: expanded remotely)
BLENDER_VERSION="${BLENDER_VERSION:-5.2.3}"
TARBALL="blender-${BLENDER_VERSION}-linux-x64.tar.xz"

SSH=(ssh -p "$GPU_PORT" -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30 -o ConnectTimeout=20)
[ -f "$GPU_KEY" ] && SSH+=(-i "$GPU_KEY" -o IdentitiesOnly=yes)
RSH="${SSH[*]}"
remote() { "${SSH[@]}" "$GPU_USER@$GPU_HOST" "$@"; }
rsync_to() { rsync -az -e "$RSH" "$@"; }
need_key() { [ -f "$GPU_KEY" ] || { echo "Belum ada kunci. Jalankan: bash andai/gpu/gpu.sh kunci"; exit 1; }; }

cmd="${1:-bantuan}"; shift || true
case "$cmd" in
  kunci)      # one-time per server: create the project key and install it (asks for the server password once)
    [ -f "$GPU_KEY" ] || ssh-keygen -t ed25519 -N '' -f "$GPU_KEY" -C "andai-gpu@$(hostname)" -q
    ssh-copy-id -i "$GPU_KEY.pub" -p "$GPU_PORT" -o StrictHostKeyChecking=accept-new "$GPU_USER@$GPU_HOST"
    remote 'echo "login dengan kunci OK: $(whoami)@$(hostname)"' ;;
  status)
    remote 'echo "host: $(hostname)  up: $(uptime -p)"; nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used --format=csv,noheader 2>&1 | head -4;
            B=$(ls -d ~/blender/blender-*/blender 2>/dev/null | head -1); [ -n "$B" ] && "$B" --version | head -1 || echo "Blender: belum terpasang";
            df -h ~ | tail -1' ;;
  kirim)      # code + episode inputs go from here to the server (outputs and caches never go this way)
    remote "mkdir -p ~/$REMOTE_DIR"
    rsync_to --delete --exclude '.git' --exclude '__pycache__' --exclude 'node_modules' --exclude 'hasil*/' \
      --exclude 'andai/gpu/gpu.env' --exclude 'episodes/*/build/' --exclude 'episodes/*/output/' \
      "$REPO/" "$GPU_USER@$GPU_HOST:$REMOTE_DIR/" && echo "kode terkirim ke $GPU_HOST:~/$REMOTE_DIR" ;;
  siapkan)    # a fresh server: send code, install Blender (download, or the local copy), run the benchmark
    need_key; "$0" kirim
    EXTRA=""
    if ! remote "ls $BLENDER_ROOT/blender-*/blender >/dev/null 2>&1"; then
      if [ "${BLENDER_DARI_CADANGAN:-0}" = "1" ] || ! remote 'curl -fsI -m 20 https://download.blender.org/release/ >/dev/null'; then
        echo "memakai cadangan Blender di $ASET/blender (bukan download.blender.org)"
        [ -f "$ASET/blender/$TARBALL" ] || { echo "Cadangan tidak ada. Jalankan di mesin ini: bash andai/gpu/gpu.sh cache-blender"; exit 1; }
        rsync_to "$ASET/blender/$TARBALL" "$GPU_USER@$GPU_HOST:$REMOTE_DIR/$TARBALL"
        EXTRA="BLENDER_TARBALL=\$HOME/$REMOTE_DIR/$TARBALL"
      fi
    fi
    remote "cd ~/$REMOTE_DIR && $EXTRA BLENDER_ROOT=$BLENDER_ROOT SKIP_BENCH=${SKIP_BENCH:-0} bash andai/gpu/setup_server.sh" ;;
  jalankan)   # run any command inside the project folder on the server; `blender` is on PATH
    remote "export PATH=\$HOME/.local/bin:\$PATH; cd ~/$REMOTE_DIR && $*" ;;
  ambil)      # fetch a server folder/file into the asset store: ambil andai/blender/hasil_pemeran [tujuan]
    src="${1:?folder remote relatif ke $REMOTE_DIR}"; dst="${2:-$ASET/render/$(basename "$src")}"
    mkdir -p "$dst"; rsync_to "$GPU_USER@$GPU_HOST:$REMOTE_DIR/$src/" "$dst/" && echo "disalin ke $dst" ;;
  cadangan)   # pull every render output and shot cache to the asset store (additive: never deletes local files)
    mkdir -p "$ASET/render"
    for d in $(remote "cd ~/$REMOTE_DIR && ls -d andai/blender/hasil* andai/gpu/hasil episodes/*/build episodes/*/output 2>/dev/null" || true); do
      mkdir -p "$ASET/render/$d"; rsync_to "$GPU_USER@$GPU_HOST:$REMOTE_DIR/$d/" "$ASET/render/$d/"; echo "dicadangkan: $d"
    done
    date -u +"cadangan terakhir: %F %T UTC dari $GPU_HOST" > "$ASET/render/CADANGAN_TERAKHIR.txt"
    echo "selesai -> $ASET/render" ;;
  pulihkan)   # new server after a crash: put the saved shot caches / outputs back so finished shots are not re-rendered
    for d in "$ASET"/render/episodes/*/; do
      [ -d "$d" ] || continue; ep="$(basename "$d")"
      remote "mkdir -p ~/$REMOTE_DIR/episodes/$ep" && rsync_to "$d" "$GPU_USER@$GPU_HOST:$REMOTE_DIR/episodes/$ep/" && echo "dipulihkan: episodes/$ep"
    done ;;
  snapshot)   # dated tarball of the project (code, episodes, docs) in the asset store
    mkdir -p "$ASET/snapshot"; f="$ASET/snapshot/Video-editor-$(date -u +%F-%H%M).tar.gz"
    tar -C "$(dirname "$REPO")" --exclude='__pycache__' --exclude='node_modules' --exclude='hasil*' --exclude='andai/gpu/gpu.env' \
      -czf "$f" "$(basename "$REPO")" && echo "snapshot: $f ($(du -h "$f" | cut -f1))" ;;
  cache-blender)   # keep our own copy of the exact Blender build, so a new server never depends on blender.org
    mkdir -p "$ASET/blender"
    [ -f "$ASET/blender/$TARBALL" ] || curl -fL -o "$ASET/blender/$TARBALL" \
      "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/$TARBALL"
    (cd "$ASET/blender" && sha256sum "$TARBALL" > "$TARBALL.sha256" && cat "$TARBALL.sha256") ;;
  uji)        # quick end-to-end check on the current server
    "$0" jalankan "bash andai/blender/uji_karakter.sh andai/blender/hasil 32 && ~/blender/blender-*/blender -b --python andai/blender/uji_keyframe.py 2>&1 | grep -E 'ALL OK|FAIL'" ;;
  *) sed -n '2,10p' "$0" ;;
esac
