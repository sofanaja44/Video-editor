#!/usr/bin/env bash
# Render the character test sheets and tile the 12 expressions into one image.
# Usage, from the repo root:  bash andai/blender/uji_karakter.sh [OUT_DIR] [SAMPLES]
set -euo pipefail
OUT="${1:-andai/blender/hasil}"; SAMPLES="${2:-48}"
mkdir -p "$OUT"
"${BLENDER:-blender}" -b --python andai/blender/uji_karakter.py -- "$OUT" "$SAMPLES" 2>&1 | grep -vE "^(Blender|Read|Warning|WARNING|\s*$)|HIPEW|Fra:|Saved|Time:" || true
ffmpeg -y -loglevel error -pattern_type glob -i "$OUT/ekspresi_*.png" -filter_complex "tile=4x3" "$OUT/ekspresi.png"
echo "Selesai: $OUT/poses.png  cast.png  ekspresi.png  kedip.png"
