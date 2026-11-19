"""Small, non-interactive wrapper around the repository's Copier questionnaire."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys

import yaml

from ats import __version__

REPOSITORY = "https://github.com/Mappedinfo/academic-templates.git"


def template_root() -> Path:
    bundled = Path(__file__).parent / "_templates"
    if (bundled / "copier.yml").is_file():
        return bundled
    # Editable/source development also uses the canonical repository files.
    source = Path(__file__).resolve().parents[2]
    if (source / "copier.yml").is_file():
        return source
    raise ValueError("Packaged Copier templates are missing; reinstall mappedinfo-ats")


def questionnaire(root: Path) -> dict:
    return yaml.safe_load((root / "copier.yml").read_text(encoding="utf-8"))


def templates(root: Path) -> dict[str, str]:
    choices = questionnaire(root)["template"]["choices"]
    return {value: label for label, value in choices.items()}


def initialize(template: str, destination: str, values: list[str]) -> Path:
    root = template_root()
    questions = questionnaire(root)
    if template not in templates(root):
        raise ValueError(f"Unknown template {template!r}; run 'ats list'")
    target = Path(os.path.abspath(Path(destination).expanduser()))
    if os.path.lexists(target):
        raise ValueError(f"Destination already exists: {target}; choose a new directory")
    data = {"template": template, "project_name": target.name}
    for value in values:
        key, separator, answer = value.partition("=")
        if not separator or key.startswith("_") or key == "template" or key not in questions:
            raise ValueError(f"Invalid --data {value!r}; use a questionnaire key and KEY=VALUE")
        data[key] = answer

    from copier import Settings, run_copy
    from copier.errors import CopierError

    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation rejects existing directories, files, and dangling symlinks.
    target.mkdir()
    try:
        run_copy(
            str(root),
            target,
            data=data,
            defaults=True,
            quiet=True,
            overwrite=False,
            unsafe=False,
            skip_tasks=True,
            settings=Settings(defaults={}, trust=[]),
            cleanup_on_error=False,
        )
        # These templates already emit Copier's complete answers. Replace the
        # installation-specific source path with the corresponding Git release.
        answers_path = target / ".copier-answers.yml"
        if answers_path.is_file():
            answers = yaml.safe_load(answers_path.read_text(encoding="utf-8"))
            answers.update(_src_path=REPOSITORY, _commit=f"v{__version__}")
            answers_path.write_text(
                yaml.safe_dump(answers, allow_unicode=True, sort_keys=False), encoding="utf-8"
            )
    except CopierError as error:
        shutil.rmtree(target)
        raise ValueError(str(error)) from error
    except BaseException:
        shutil.rmtree(target)
        raise
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ats", description="Academic Template Starter")
    parser.add_argument("--version", action="version", version=f"ats {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List bundled Copier templates")
    init = commands.add_parser("init", help="Create a project in a new directory")
    init.add_argument("template", help="Template name from 'ats list'")
    init.add_argument("destination", help="New project directory")
    init.add_argument("--data", "-d", action="append", default=[], metavar="KEY=VALUE",
                      help="Override a Copier answer; may be repeated")
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            for name, label in templates(template_root()).items():
                print(f"{name}\t{label}")
        else:
            target = initialize(args.template, args.destination, args.data)
            print(f"Created {target} from {args.template} (ATS {__version__})")
        return 0
    except (OSError, ValueError) as error:
        print(f"ats: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("ats: initialization cancelled", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
