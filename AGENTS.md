# Agents notes for academic-templates

- Multi-template copier repo: each top-level dir (except `fonts/`, `shared/` and
  `scripts/`) is a standalone copier template with its own `copier.yml` +
  `template/`.
- Root `copier.yml` enables remote use (`copier copy gh:mappedinfo/academic-templates`):
  it asks which template via a `template` choice and sets `_subdirectory`
  accordingly, with per-template conditional questions (`when`). When adding or
  changing questions in a per-template `copier.yml`, mirror them in the root
  `copier.yml`.
- Empty dirs are invisible to git: any `template/` dir that must exist in
  generated projects needs a `.gitkeep`, or the remote (gh:) flow drops it.
- Only `*.jinja` files are rendered by copier; everything else is copied
  verbatim. LaTeX/Quarto files with braces are safe as long as they do not
  contain `{{ }}` sequences.
- Font baseline is Libertinus + Noto CJK SC, canonicalized in `fonts/`.
  Templates embed copies of the font include files so generated projects are
  self-contained; update `fonts/` first, then sync the copies.
- Shared assets have one canonical source and byte-identical per-template
  copies: `fonts/` owns the font baseline, `shared/` owns shared experiment
  tooling (see `shared/README.md`). Edit the canonical file, then run
  `./scripts/sync-shared.sh`; `./scripts/sync-shared.sh --check` fails on drift
  and is the guard against the hand-sync failures this repo already had.
- A template receives a shared asset only if it already carries that path
  (`scripts/`, `config/`, `latex-fonts.tex`). For a generic target filename such
  as `.gitignore`, the entry must instead name its templates in the optional
  third field — otherwise the sync claims another template's own hand-written
  file and overwrites it. A new template needs the copy placed once, and a
  genuinely new shared asset registered in the `ASSETS` array of
  `scripts/sync-shared.sh`.
- Shared `scripts/*.py` are copied verbatim, not rendered: keep them free of
  `{{ }}` sequences and of absolute paths. Resolve project paths from
  `Path(__file__).resolve().parent.parent` so they work in every template.
- Test a template: `uvx copier copy --defaults <template-dir> /tmp/out`.
