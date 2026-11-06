import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / 'shared/data-exploration/scripts/check_dependencies.py'
spec = importlib.util.spec_from_file_location('check_dependencies', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DependencyChecks(unittest.TestCase):
    def simulate(self, available, r_installed=True, mac=True):
        def fake_probe(command, cwd):
            if command[0] == 'pkgutil':
                return False
            if command[0] == 'Rscript':
                key = Path(command[-1]).stem
                output = Path(command[-1])
            else:
                key = 'python_matplotlib'
                output = Path(command[-1])
            if key in available:
                output.write_text('figure')
                return True
            return False
        with patch.object(module.shutil, 'which', return_value='Rscript' if r_installed else None), \
             patch.object(module.platform, 'system', return_value='Darwin' if mac else 'Linux'), \
             patch.object(module, 'probe', side_effect=fake_probe):
            return module.check()

    def test_svglite_available_without_native_svg(self):
        result = self.simulate({'r_svglite'})
        self.assertTrue(result['plot_available'])
        self.assertTrue(result['r_svglite'])
        self.assertFalse(result['r_svg'])

    def test_pdf_is_valid_fallback(self):
        result = self.simulate({'r_pdf'})
        self.assertTrue(result['plot_available'])
        self.assertFalse(result['r_svg'])

    def test_python_works_without_r_or_xquartz(self):
        result = self.simulate({'python_matplotlib'}, r_installed=False)
        self.assertTrue(result['plot_available'])
        self.assertFalse(result['r_installed'])

    def test_no_graphics_still_explains_text_reports(self):
        result = self.simulate(set())
        self.assertFalse(result['plot_available'])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            module.display(result)
        self.assertIn('文字报告', output.getvalue())
        self.assertIn('brew install --cask xquartz', output.getvalue())

    def test_linux_does_not_suggest_xquartz(self):
        result = self.simulate(set(), mac=False)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            module.display(result)
        self.assertNotIn('brew install --cask xquartz', output.getvalue())

    def test_missing_executables_does_not_fail_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], env={**os.environ, 'PATH': ''},
                                capture_output=True, text=True, timeout=40)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('R 自带 SVG: 不可用', result.stdout)


if __name__ == '__main__':
    unittest.main()
