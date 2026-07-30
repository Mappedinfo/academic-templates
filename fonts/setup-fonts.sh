#!/usr/bin/env bash
# Install the academic-templates font baseline.
# macOS (Homebrew) by default; Debian/Ubuntu alternative noted below.
set -euo pipefail

if [[ "$(uname)" == "Darwin" ]]; then
  brew install --cask \
    font-noto-serif-cjk-sc \
    font-noto-sans-cjk-sc \
    font-libertinus \
    font-libertinus-sans \
    font-libertinus-math
  echo "Fonts installed to /Library/Fonts (system-wide)."
else
  cat <<'EOF'
Debian/Ubuntu:
  sudo apt install fonts-noto-cjk fonts-noto-cjk-extra
  # Libertinus: https://github.com/alerque/libertinus/releases (OTF into ~/.local/share/fonts)
  # then: fc-cache -f
EOF
  exit 1
fi
