from __future__ import annotations
import json
import csv
import importlib.util
import shutil
import sys
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

NOTEBOOK = Path(__file__).resolve().parents[2] / 'shared/data-exploration/analysis.ipynb'

class NotebookTemplateTests(unittest.TestCase):
    def setUp(self):
        self.nb = json.loads(NOTEBOOK.read_text(encoding='utf-8'))
        self.code = ''.join(self.nb['cells'][1]['source'])
        self.tmp = tempfile.TemporaryDirectory()
        self.old_cwd = Path.cwd()
        os.chdir(self.tmp.name)
    def tearDown(self):
        os.chdir(self.old_cwd)
        self.tmp.cleanup()
    def configured(self):
        return (self.code.replace('RUN_REMOTE = False', 'RUN_REMOTE = True')
                .replace('SSH_ALIAS = ""', 'SSH_ALIAS = "worker"')
                .replace('REMOTE_COMMAND = []', 'REMOTE_COMMAND = ["python3", "aggregate.py"]')
                .replace('REMOTE_FILE = ""', 'REMOTE_FILE = "/remote/summary.csv"'))
    def test_default_never_contacts_ssh(self):
        with patch('subprocess.run') as call:
            exec(self.code, {})
            call.assert_not_called()
    def test_remote_success_saves_data_and_uses_argument_arrays(self):
        calls = []
        def run(args, **kwargs):
            calls.append(args)
            if 'stdout' in kwargs: kwargs['stdout'].write(b'x,y\n1,2\n')
            return subprocess.CompletedProcess(args, 0)
        with patch('subprocess.run', side_effect=run): exec(self.configured(), {})
        self.assertEqual(Path('plot-data/summary.csv').read_text(), 'x,y\n1,2\n')
        self.assertEqual(calls[0], ['ssh', 'worker', 'python3 aggregate.py'])
        self.assertEqual(calls[1], ['ssh', 'worker', 'cat -- /remote/summary.csv'])
    def test_existing_local_file_is_never_replaced(self):
        path = Path('plot-data/summary.csv'); path.parent.mkdir(); path.write_text('existing')
        with patch('subprocess.run') as call:
            with self.assertRaises(FileExistsError): exec(self.configured(), {})
            call.assert_not_called()
        self.assertEqual(path.read_text(), 'existing')
    def test_failed_transfer_removes_only_its_partial_file(self):
        def run(args, **kwargs):
            if 'stdout' in kwargs:
                kwargs['stdout'].write(b'partial')
                raise subprocess.CalledProcessError(1, args)
            return subprocess.CompletedProcess(args, 0)
        with patch('subprocess.run', side_effect=run):
            with self.assertRaises(subprocess.CalledProcessError): exec(self.configured(), {})
        self.assertFalse(Path('plot-data/summary.csv').exists())
    def test_cells_are_valid_python(self):
        for cell in self.nb['cells']:
            if cell['cell_type'] == 'code': compile(''.join(cell['source']), '<notebook>', 'exec')

class ScriptIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('Rscript'), 'R unavailable')
    def test_svg_redraw_from_local_summary(self):
        available = subprocess.run(['Rscript', '-e', 'quit(status=if (requireNamespace("svglite", quietly=TRUE)) 0 else 2)'], capture_output=True)
        if available.returncode != 0:
            self.skipTest('svglite unavailable; SVG fallback is environment dependent')
        root = NOTEBOOK.parent
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory); source = tmp / 'summary.csv'; output = tmp / 'summary.svg'
            source.write_text('hour,count\n08,12\n09,18\n10,7\n')
            before = source.read_bytes()
            result = subprocess.run(['Rscript', str(root/'scripts/plot.R'), str(source), 'hour', 'count', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('<svg', output.read_text())
            self.assertEqual(before, source.read_bytes())
            self.assertNotEqual(subprocess.run(['Rscript', str(root/'scripts/plot.R'), str(source), 'hour', 'count', str(output)], capture_output=True).returncode, 0)

    @unittest.skipUnless(importlib.util.find_spec('pandas'), 'pandas unavailable')
    @unittest.skipUnless(shutil.which('Rscript'), 'R unavailable')
    def test_real_csv_summary_and_r_plot(self):
        root = NOTEBOOK.parent
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            original = temp / 'raw.csv'
            original.write_text('group,value\nA,1\nA,0\nA,\nB,5\nB,NA\n')
            before = original.read_bytes()
            summary = temp / 'summary.csv'
            command = [sys.executable, str(root/'scripts/summarize.py'), '--input', str(original),
                       '--group', 'group', '--value', 'value', '--missing-token', 'NA',
                       '--output', str(summary), '--chunk-size', '2']
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            with summary.open() as handle: rows = {row['group']: row for row in csv.DictReader(handle)}
            self.assertEqual((rows['A']['rows'], rows['A']['valid'], rows['A']['zeros'], rows['A']['missing']), ('3','2','1','1'))
            self.assertEqual(float(rows['A']['mean']), 0.5)
            self.assertEqual((rows['B']['rows'], rows['B']['missing'], float(rows['B']['mean'])), ('2','1',5.0))
            image = temp/'summary.pdf'
            result = subprocess.run(['Rscript', str(root/'scripts/plot.R'), str(summary), 'group', 'mean', str(image)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(image.read_bytes().startswith(b'%PDF'))
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(original.read_bytes(), before)

if __name__ == '__main__': unittest.main()
