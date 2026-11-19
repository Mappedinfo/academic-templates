"""Bundle the canonical Copier files at build time; never maintain a second copy."""

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class TemplateBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        root = Path(self.root)
        paths = [root / "copier.yml"]
        for directory in sorted(root.iterdir()):
            if (directory / "copier.yml").is_file() and (directory / "template").is_dir():
                paths.extend([directory / "copier.yml", directory / "template"])
        if len(paths) == 1:
            raise RuntimeError("No canonical Copier templates found")
        for path in paths:
            relative = path.relative_to(root).as_posix()
            target = f"ats/_templates/{relative}" if self.target_name == "wheel" else relative
            build_data["force_include"][str(path)] = target
