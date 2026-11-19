"""Smoke-test an installed ATS executable, with the working directory outside source."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    executable = str(Path(sys.argv[1]).resolve())
    with TemporaryDirectory(prefix="ats-smoke-") as directory:
        root = Path(directory)

        def ats(*args):
            return subprocess.run([executable, *args], cwd=root, capture_output=True, text=True)

        listed = ats("list")
        assert listed.returncode == 0, listed.stderr
        names = {line.split("\t")[0] for line in listed.stdout.splitlines()}
        assert names == {"report", "literature-review", "paper", "paper-replication",
                         "dev-project", "paper-with-code", "brainstorm"}, names
        generated = ats("init", "paper-with-code", "my-paper", "-d", "title=Smoke Paper")
        assert generated.returncode == 0, generated.stderr
        project = root / "my-paper"
        for name in ["README.md", "Makefile", ".copier-answers.yml", "paper/main.tex",
                     "paper/latex-fonts.tex", "paper/sections/03-method.tex",
                     "code/pyproject.toml", "code/src/my_paper/__init__.py",
                     "experiments/.gitkeep", "scripts/run_experiments.py"]:
            assert (project / name).is_file(), name
        assert "Smoke Paper" in (project / "paper/main.tex").read_text()
        answers = (project / ".copier-answers.yml").read_text()
        assert "https://github.com/Mappedinfo/academic-templates.git" in answers
        assert "_commit: v" in answers
        assert not (project / "experiments/results").exists(), "Initialization ran experiments"
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        refused = ats("init", "paper-with-code", "my-paper")
        assert refused.returncode != 0 and "already exists" in refused.stderr, refused
        after = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        assert before == after, "Existing project changed"
        (root / "empty").mkdir()
        assert ats("init", "paper-with-code", "empty").returncode != 0
        assert not list((root / "empty").iterdir())
        (root / "link").symlink_to(root / "missing", target_is_directory=True)
        assert ats("init", "paper-with-code", "link").returncode != 0
        assert (root / "link").is_symlink() and not (root / "missing").exists()
        print("PASS: installed list, paper-with-code scaffold, no experiments, existing paths unchanged")


if __name__ == "__main__":
    main()
