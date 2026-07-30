#!/usr/bin/env bash
# Direct-download installer for the academic-templates font baseline.
# Use when `brew install --cask` fails on the large Noto CJK downloads.
# Same release zips as the brew casks, but with resume (-C -) and retries,
# so a flaky connection can complete across multiple runs.
# Installs Regular+Bold weights to ~/Library/Fonts (user-level, no sudo). macOS only.
set -euo pipefail

DEST="$HOME/Library/Fonts"
WORK="$HOME/.cache/academic-templates-fonts"
mkdir -p "$DEST" "$WORK"

GH="https://github.com/notofonts/noto-cjk/releases/download"

fetch() { # fetch <url> <outfile> — resumable
  echo "== $(basename "$2") =="
  curl -sL -C - --retry 10 --retry-all-errors --retry-delay 3 -o "$2" "$1"
}

# Serif CJK SC (zip has nested OTF/SimplifiedChinese/ paths)
fetch "$GH/Serif2.003/09_NotoSerifCJKsc.zip" "$WORK/09_NotoSerifCJKsc.zip"
unzip -o -j "$WORK/09_NotoSerifCJKsc.zip" \
  "OTF/SimplifiedChinese/NotoSerifCJKsc-Regular.otf" \
  "OTF/SimplifiedChinese/NotoSerifCJKsc-Bold.otf" -d "$DEST"

# Sans CJK SC (flat zip)
fetch "$GH/Sans2.004/08_NotoSansCJKsc.zip" "$WORK/08_NotoSansCJKsc.zip"
unzip -o -j "$WORK/08_NotoSansCJKsc.zip" \
  "NotoSansCJKsc-Regular.otf" "NotoSansCJKsc-Bold.otf" -d "$DEST"

# Sans Mono CJK SC (flat zip)
fetch "$GH/Sans2.004/10_NotoSansMonoCJKsc.zip" "$WORK/10_NotoSansMonoCJKsc.zip"
unzip -o -j "$WORK/10_NotoSansMonoCJKsc.zip" \
  "NotoSansMonoCJKsc-Regular.otf" "NotoSansMonoCJKsc-Bold.otf" -d "$DEST"

# Libertinus (Latin + math)
fetch "https://github.com/alerque/libertinus/releases/download/v7.051/Libertinus-7.051.zip" \
  "$WORK/Libertinus-7.051.zip"
unzip -q -o "$WORK/Libertinus-7.051.zip" -d "$WORK/libertinus"
find "$WORK/libertinus" \( -name "*.otf" -o -name "*.ttf" \) -exec cp {} "$DEST/" \;

echo "Installed fonts to $DEST:"
ls -1 "$DEST" | grep -iE "noto|libertinus" || true
echo "Interrupted downloads can be resumed by simply re-running this script."
echo "matplotlib users: rm -rf ~/.matplotlib/fontlist-*.json to rebuild the font cache"
