"""Verify independent exact scoring without any CLI/model calls."""
import importlib.util
import json
import pathlib
import unittest
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = pathlib.Path(__file__).parent / 'fixtures' / 'model-selection-2175'
spec = importlib.util.spec_from_file_location('score2175', ROOT / 'score.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.path.insert(0, str(ROOT))
import runner


class ExactOracleTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / 'fixtures.json').read_text(encoding='utf-8'))['cases']
        self.expected = {case['id']: case['answer'] for case in self.cases}

    def test_exact_and_single_error(self):
        result = module.score(json.dumps(self.expected), self.cases)
        self.assertTrue(result['pass'])
        self.assertEqual((result['correct'], result['total']), (12, 12))
        self.expected['E1'] = 'wrong'
        result = module.score(json.dumps(self.expected), self.cases)
        self.assertFalse(result['pass'])
        self.assertEqual((result['correct'], result['total']), (11, 12))

    def test_denominator_on_invalid_responses(self):
        missing = dict(self.expected)
        missing.pop('E1')
        extra = dict(self.expected, unexpected='x')
        nonstring = dict(self.expected, E1=44)
        duplicate = json.dumps(self.expected)[:-1] + ', "E1": "T-044"}'
        for text in [json.dumps(missing), json.dumps(extra), json.dumps(nonstring), duplicate, '[]', 'bad']:
            with self.subTest(text=text):
                result = module.score(text, self.cases)
                self.assertFalse(result['pass'])
                self.assertEqual((result['correct'], result['total']), (0, 12))

    def test_duplicate_oracle_rejected(self):
        with self.assertRaises(ValueError):
            module.score('{}', [self.cases[0], self.cases[0]])

    def test_manifest_coverage(self):
        manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
        ids = [key for batch in manifest['batches'] for key in batch['ids']]
        self.assertEqual(len(ids), 12)
        self.assertEqual(set(ids), set(self.expected))
        self.assertEqual(len(set(ids)), len(ids))

    def test_failed_launch_preserves_attempt_and_unknown_cost(self):
        for error in [subprocess.TimeoutExpired('synthetic', 180), OSError('synthetic')]:
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                raw = pathlib.Path(directory) / 'raw'
                raw.mkdir()
                out = pathlib.Path(directory) / 'not-created' / 'attempt.json'
                argv = ['runner.py','--model','haiku','--batch','1','--cli','synthetic',
                        '--raw-dir',str(raw),'--out',str(out),'--execute']
                with patch.object(sys,'argv',argv), patch.object(runner.subprocess,'run',side_effect=error) as launch:
                    with self.assertRaises(SystemExit):
                        runner.main()
                record = json.loads(out.read_text(encoding='utf-8'))
                self.assertIsNone(record['reported_total_cost_usd'])
                self.assertEqual(record['requested_model'],'haiku')
                self.assertIn(record['error_class'],['timeout','os_error'])
                self.assertEqual(len(list(raw.glob('*.attempt.json'))),1)
                launch.assert_called_once()

    def test_separated_fixture_coverage_and_conditional_handoff(self):
        separated = ROOT.parent / 'model-selection-2175-separated'
        fixtures = json.loads((separated/'fixtures.json').read_text(encoding='utf-8'))['cases']
        self.assertEqual(len(fixtures),8)
        for category in ['extraction','known-text-retrieval']:
            selected = [case for case in fixtures if case['category']==category]
            self.assertEqual(len(selected),4)
            self.assertEqual([case['language'] for case in selected].count('ja'),2)
            self.assertEqual([case['language'] for case in selected].count('en'),2)
        manifest = json.loads((separated/'manifest.json').read_text(encoding='utf-8'))
        oracle = manifest['batches'][0]['oracle']
        previous = {'requested_model':'haiku','effort':'low','batch':1,'exit_code':0,
                    'prompt_sha256':manifest['batches'][0]['prompt_sha256'],
                    'model_usage':{'claude-haiku-5-5':{}},'answer':json.dumps(oracle)}
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory)/'previous.json'
            raw = pathlib.Path(directory)/'raw'
            out = pathlib.Path(directory)/'out.json'
            argv = ['runner.py','--fixture-dir',str(separated),'--model','opus','--batch','1',
                    '--cli','synthetic','--raw-dir',str(raw),'--out',str(out),
                    '--handoff-from',str(source),'--execute']
            source.write_text(json.dumps(previous),encoding='utf-8')
            with patch.object(sys,'argv',argv), patch.object(runner.subprocess,'run') as launch:
                with self.assertRaises(SystemExit):
                    runner.main()
                launch.assert_not_called()
            wrong = dict(oracle,SE1='wrong')
            previous['answer'] = json.dumps(wrong)
            source.write_text(json.dumps(previous),encoding='utf-8')
            response = {'is_error':False,'result':json.dumps(oracle),'total_cost_usd':0.02,
                        'usage':{key:1 for key in ['input_tokens','output_tokens','cache_creation_input_tokens','cache_read_input_tokens']},
                        'modelUsage':{'claude-opus-5-5':{'costUSD':0.02}}}
            proc = types.SimpleNamespace(returncode=0,stdout=json.dumps(response),stderr='')
            with patch.object(sys,'argv',argv), patch.object(runner.subprocess,'run',return_value=proc) as launch:
                runner.main()
                prompt = launch.call_args.args[0][-1]
                self.assertIn(previous['answer'],prompt)
                self.assertIn('failed case ids',prompt)
                self.assertIn('["SE1"]',prompt)
            record = json.loads(out.read_text(encoding='utf-8'))
            self.assertEqual(record['kind'],'correction')
            self.assertTrue(record['score']['pass'])
            self.assertIn('validator_duration_seconds',record)
            out.unlink()
            with patch.object(sys,'argv',argv), patch.object(runner.subprocess,'run') as launch:
                with self.assertRaises(SystemExit):
                    runner.main()
                launch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
