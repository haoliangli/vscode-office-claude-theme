#!/usr/bin/env bash
# Build a Claude-themed cweijan.vscode-office .vsix by overlaying the Claude theme
# onto your already-installed (prebuilt) extension. No source rebuild required —
# the change is purely additive static assets + a couple of patches, so we
# repackage the compiled artifact and skip the upstream build toolchain.
#
# Usage: scripts/build.sh [BASE_EXTENSION_DIR]
#   BASE_EXTENSION_DIR   installed cweijan.vscode-office dir (auto-detected if omitted)
#   FONT_SRC (env var)   directory to source the OPTIONAL Anthropic + Noto Serif SC
#                        fonts from, for the exact Claude look. Fonts are NOT shipped
#                        with this repo (Anthropic fonts are proprietary; see README).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="$HERE/_build"
DIST="$HERE/dist"
FONTS_DST="$BUILD/resource/vditor/css/fonts"

# --- locate the installed extension ---
BASE="${1:-}"
if [ -z "$BASE" ]; then
  BASE="$(ls -d "$HOME/.vscode/extensions/cweijan.vscode-office-"* 2>/dev/null | sort -V | tail -1 || true)"
fi
echo "[1/6] base = ${BASE:-<none>}"
{ [ -n "$BASE" ] && [ -d "$BASE" ]; } || { echo "ERROR: cweijan.vscode-office not found. Install it from the Marketplace first, or pass its directory as arg 1."; exit 1; }

echo "[2/6] copy base -> _build"
rm -rf "$BUILD"; mkdir -p "$BUILD" "$DIST"
cp -R "$BASE/." "$BUILD/"
rm -f "$BUILD/.vsixmanifest"   # install-time artifact; vsce regenerates its own

echo "[3/6] apply overlay (theme CSS + any fonts you supplied)"
cp -R "$HERE/overlay/." "$BUILD/"
mkdir -p "$FONTS_DST"

# --- source OPTIONAL fonts. Precedence: fonts you dropped in overlay/.../fonts/
#     > FONT_SRC. Missing fonts just fall back to open/system serifs. ---
FONT_SRC="${FONT_SRC:-$HOME/Library/Application Support/abnerworks.Typora/themes/old-themes/claude-theme/claude_fonts}"
for f in AnthropicSerifWebText.ttf AnthropicSansWebText.ttf AnthropicMonoVariable.ttf NotoSerifSC-VariableFont_wght.ttf; do
  if [ -f "$FONTS_DST/$f" ]; then
    echo "  + $f (from overlay)"
  elif [ -f "$FONT_SRC/$f" ]; then
    cp "$FONT_SRC/$f" "$FONTS_DST/$f" && echo "  + $f (from FONT_SRC)"
  else
    echo "  - $f absent -> fallback serif (see README to get exact Claude fonts)"
  fi
done

echo "[4/6] inject enum + base.css outline + @font-face + extension.js quick-pick"
python3 "$HERE/scripts/inject.py" "$BUILD"

echo "[5/6] package vsix"
VER="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]+"/package.json"))["version"])' "$BUILD")"
OUT="$DIST/cweijan.vscode-office-${VER}-claude.vsix"
rm -f "$OUT"
( cd "$BUILD" && npx --yes @vscode/vsce package --no-dependencies --allow-missing-repository -o "$OUT" < /dev/null )

echo "[6/6] done -> $OUT"
echo
echo "Install:  code --install-extension \"$OUT\" --force"
echo "Then: Reload Window, set vscode-office.editorTheme = Claude (or Claude Dark),"
echo "and disable auto-update for cweijan.vscode-office so it isn't overwritten."
