# Agents notes for academic-templates

- Multi-template copier repo: each top-level dir (except `fonts/`) is a
  standalone copier template with its own `copier.yml` + `template/`.
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
- Test a template: `uvx copier copy --defaults <template-dir> /tmp/out`.
