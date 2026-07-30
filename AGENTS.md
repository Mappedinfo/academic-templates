# Agents notes for academic-templates

- Multi-template copier repo: each top-level dir (except `fonts/`) is a
  standalone copier template with its own `copier.yml` + `template/`.
- Only `*.jinja` files are rendered by copier; everything else is copied
  verbatim. LaTeX/Quarto files with braces are safe as long as they do not
  contain `{{ }}` sequences.
- Font baseline is Libertinus + Noto CJK SC, canonicalized in `fonts/`.
  Templates embed copies of the font include files so generated projects are
  self-contained; update `fonts/` first, then sync the copies.
- Test a template: `uvx copier copy --defaults <template-dir> /tmp/out`.
