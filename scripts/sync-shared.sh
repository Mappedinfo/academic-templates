#!/usr/bin/env bash
# Keep every template's copy of a shared asset byte-identical to its canonical
# source. fonts/ is canonical for the font baseline, shared/ for experiment
# tooling; templates embed copies so generated projects stay self-contained.
#
#   ./scripts/sync-shared.sh          canonical -> template copies (writes)
#   ./scripts/sync-shared.sh --check  report drift and exit 1 (no writes)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-sync}"

# "canonical-relative-path:template-relative-path[:template,template]"
# The optional third field restricts the asset to named templates. Use it for
# generic target filenames such as .gitignore, where "already carries the path"
# would silently claim another template's own hand-written file.
ASSETS=(
  "fonts/matplotlib-style.mplstyle:scripts/matplotlib-style.mplstyle"
  "fonts/latex-fonts.tex:latex-fonts.tex"
  "shared/scripts/fetch_and_plot.py:scripts/fetch_and_plot.py"
  "shared/config/urls.example.txt:config/urls.example.txt"
  "shared/gitignore:.gitignore:paper,paper-with-code,paper-replication,report"
  "shared/data-exploration/README.md:analysis/data-exploration/README.md:paper-replication,paper-with-code"
  "shared/data-exploration/analysis.ipynb:analysis/data-exploration/analysis.ipynb:paper-replication,paper-with-code"
  "shared/data-exploration/scripts/summarize.py:analysis/data-exploration/scripts/summarize.py:paper-replication,paper-with-code"
  "shared/data-exploration/scripts/plot.R:analysis/data-exploration/scripts/plot.R:paper-replication,paper-with-code"
  "shared/data-exploration/plot-data/.gitignore:analysis/data-exploration/plot-data/.gitignore:paper-replication,paper-with-code"
  "shared/data-exploration/figures/.gitignore:analysis/data-exploration/figures/.gitignore:paper-replication,paper-with-code"
)

drift=0
changed=0
for entry in "${ASSETS[@]}"; do
  src_rel="${entry%%:*}"
  rest="${entry#*:}"
  if [ "$rest" = "${rest%%:*}" ]; then
    dst_rel="$rest"
    only=""
  else
    dst_rel="${rest%%:*}"
    only="${rest#*:}"
  fi
  src="$ROOT/$src_rel"
  if [ ! -f "$src" ]; then
    echo "missing canonical source: $src_rel" >&2
    exit 2
  fi
  for template_dir in "$ROOT"/*/; do
    [ -f "$template_dir/copier.yml" ] || continue   # skip fonts/, shared/, scripts/
    name="$(basename "$template_dir")"
    if [ -n "$only" ]; then
      case ",$only," in
        *",$name,"*) ;;
        *) continue ;;
      esac
    fi
    dst="$template_dir/template/$dst_rel"
    [ -e "$dst" ] || continue                       # this template does not carry the asset
    if cmp -s "$src" "$dst"; then
      continue
    fi
    if [ "$MODE" = "--check" ]; then
      echo "DRIFT $name/template/$dst_rel" >&2
      drift=1
    else
      cp "$src" "$dst"
      echo "synced $name/template/$dst_rel"
      changed=1
    fi
  done
done

if [ "$MODE" = "--check" ]; then
  if [ "$drift" -eq 0 ]; then
    echo "shared assets in sync"
  fi
  exit "$drift"
fi

if [ "$changed" -eq 0 ]; then
  echo "already in sync"
else
  echo "sync complete - review with: git diff --stat"
fi
