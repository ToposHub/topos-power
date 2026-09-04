#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

ICON_SOURCE="$PROJECT_ROOT/src/topos_power/assets/topos-power-icon.png"
ICONSET_DIR="$PROJECT_ROOT/build/topos-power.iconset"
ICON_PATH="$PROJECT_ROOT/build/topos-power.icns"

if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller is not installed. Run: python3 -m pip install pyinstaller" >&2
  exit 1
fi

mkdir -p "$ICONSET_DIR"

for spec in \
  "16 16 icon_16x16.png" \
  "32 32 icon_16x16@2x.png" \
  "32 32 icon_32x32.png" \
  "64 64 icon_32x32@2x.png" \
  "128 128 icon_128x128.png" \
  "256 256 icon_128x128@2x.png" \
  "256 256 icon_256x256.png" \
  "512 512 icon_256x256@2x.png" \
  "512 512 icon_512x512.png" \
  "1024 1024 icon_512x512@2x.png"; do
  read -r width height filename <<< "$spec"
  sips -z "$height" "$width" "$ICON_SOURCE" \
    --out "$ICONSET_DIR/$filename" >/dev/null
done

iconutil -c icns "$ICONSET_DIR" -o "$ICON_PATH"

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "Topos Power" \
  --paths "$PROJECT_ROOT/src" \
  --icon "$ICON_PATH" \
  --add-data "$ICON_SOURCE:topos_power/assets" \
  --specpath "$PROJECT_ROOT/build" \
  --distpath "$PROJECT_ROOT/dist" \
  --workpath "$PROJECT_ROOT/build/pyinstaller" \
  "$PROJECT_ROOT/packaging/app_entry.py"

echo "Built: $PROJECT_ROOT/dist/Topos Power.app"
