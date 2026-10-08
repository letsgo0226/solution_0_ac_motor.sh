#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"

need() {
  command -v "$1" >/dev/null 2>&1 && return 0
  if command -v apk >/dev/null 2>&1; then
    echo "[HSI Music] installing missing dependency: $1" >&2
    apk add --no-cache "$2" >/dev/null
  else
    echo "[HSI Music] missing dependency: $1" >&2
    exit 127
  fi
}
need python3 python3

if [ "${1:-}" = "--import-render" ]; then
  [ "$#" -ge 3 ] || { echo "usage: ./hsi_music.sh --import-render URL TASK_ID [RENDERER]" >&2; exit 2; }
  URL=$2
  TASK=$3
  RENDERER=${4:-external-singing-renderer}
  exec python3 hsi_music/import_render.py "$URL" --task-id "$TASK" --renderer "$RENDERER"
fi

PROMPT=${1:-昴宿星團的藍}
shift || true
STYLE=${HSI_MUSIC_STYLE:-cinematic-pop}
LANG=${HSI_MUSIC_LANGUAGE:-zh-TW}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --style) STYLE=$2; shift 2 ;;
    --language) LANG=$2; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

echo "[HSI Music] local generation: $PROMPT"
python3 hsi_music/build.py "$PROMPT" --style "$STYLE" --language "$LANG"

echo "[HSI Music] local certificate:"
python3 - <<'PY'
import json
c=json.load(open("hsi_music.hsicert",encoding="utf-8"))
print(" protocol =",c["protocol"])
print(" music_uid =",c["music_uid"])
print(" blue_uid  =",c["blue_uid"])
print(" closed    =",c["closed"])
if c["closed"]!=1: raise SystemExit(1)
PY

if [ -n "${HSI_MUSIC_RENDER_URL:-}" ]; then
  echo "[HSI Music] remote renderer configured; submitting..."
  RESPONSE=$(python3 hsi_music/remote_render.py)
  URL=$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["url"])')
  TASK=$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("task_id") or json.load(sys.stdin).get("taskId") or "")' 2>/dev/null || true)
  if [ -z "$TASK" ]; then
    TASK=$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("task_id",d.get("taskId","remote-task")))' )
  fi
  RENDERER=$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("renderer","remote-singing-renderer"))')
  python3 hsi_music/import_render.py "$URL" --task-id "$TASK" --renderer "$RENDERER"
  echo "[HSI Music] finished: hsi_music_song.mp3"
else
  echo "[HSI Music] no HSI_MUSIC_RENDER_URL configured."
  echo "[HSI Music] local package is ready: lyrics + MIDI + vocal request + HSI certificate."
  echo "[HSI Music] to bind a finished singing render later:"
  echo "  ./hsi_music.sh --import-render 'HTTPS_AUDIO_URL' TASK_ID"
fi
