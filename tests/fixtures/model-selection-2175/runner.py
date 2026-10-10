"""One manual batch attempt; requires explicit --execute. Never retries."""
import argparse
import datetime
import json
import pathlib
import subprocess
import time

from score import score

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=['haiku', 'opus'], required=True)
    parser.add_argument('--batch', type=int, choices=[1, 2, 3], required=True)
    parser.add_argument('--cli', required=True, help='absolute path to native claude executable')
    parser.add_argument('--raw-dir', required=True, help='untracked directory outside repository')
    parser.add_argument('--out', required=True, help='sanitized attempt JSON; never raw CLI output')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    prompt = (ROOT / f'batch-{args.batch}-prompt.txt').read_text(encoding='utf-8')
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    batch = manifest['batches'][args.batch - 1]
    import hashlib
    if hashlib.sha256((ROOT / 'fixtures.json').read_text(encoding='utf-8').encode()).hexdigest() != manifest['fixture_sha256']:
        parser.error('fixture checksum mismatch')
    if hashlib.sha256(prompt.encode()).hexdigest() != batch['prompt_sha256']:
        parser.error('prompt checksum mismatch')
    argv = [args.cli, '--safe-mode', '--no-session-persistence', '--print', '--output-format', 'json',
            '--model', args.model, '--effort', 'low', '--tools', '', '--disable-slash-commands', '--strict-mcp-config', prompt]
    if not args.execute:
        print(json.dumps({'dry_run': True, 'model': args.model, 'effort': 'low', 'batch': args.batch,
                          'prompt_sha256': batch['prompt_sha256'], 'case_count': len(batch['ids'])}))
        return
    raw = pathlib.Path(args.raw_dir).resolve()
    repo = ROOT.parents[2]
    if raw == repo or repo in raw.parents:
        parser.error('raw-dir must be outside repository')
    output = pathlib.Path(args.out).resolve()
    if output.exists():
        parser.error('out already exists; retain every attempt, do not overwrite')
    output.parent.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    if len(list(raw.glob('*.attempt.json'))) >= 6:
        parser.error('six-attempt budget exhausted; retries count toward this budget')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    started = time.monotonic()
    base = {'utc':stamp,'requested_model':args.model,'effort':'low','batch':args.batch,
            'prompt_sha256':batch['prompt_sha256'],'reported_total_cost_usd':None}
    (raw / f'{stamp}.attempt.json').write_text(json.dumps(base),encoding='utf-8')
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    except (subprocess.TimeoutExpired, OSError) as error:
        # Consume one attempt even if the CLI never returns a JSON result.
        (raw / f'{stamp}.stdout.txt').write_bytes(getattr(error,'stdout',None) or b'')
        (raw / f'{stamp}.stderr.txt').write_bytes(getattr(error,'stderr',None) or b'')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({**base,
            'error_class':'timeout' if isinstance(error,subprocess.TimeoutExpired) else 'os_error','exit_code':None,
            'duration_seconds':round(time.monotonic()-started,3)},indent=2)+'\n',encoding='utf-8')
        raise SystemExit('launch failed or timed out; stop, no automatic retry')
    (raw / f'{stamp}.stdout.txt').write_text(proc.stdout, encoding='utf-8')
    (raw / f'{stamp}.stderr.txt').write_text(proc.stderr, encoding='utf-8')
    record = {**base,
              'prompt_sha256': batch['prompt_sha256'], 'exit_code': proc.returncode,
              'duration_seconds': round(time.monotonic() - started, 3), 'stderr_nonempty': bool(proc.stderr)}
    try:
        data = json.loads(proc.stdout)
        record.update({k: data[k] for k in ['is_error', 'duration_ms', 'duration_api_ms', 'total_cost_usd'] if k in data})
        record['reported_total_cost_usd'] = data.get('total_cost_usd')
        record['usage'] = {k: data.get('usage', {}).get(k) for k in ['input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens']}
        record['model_usage'] = {model: {k: details[k] for k in ['inputTokens','outputTokens','cacheReadInputTokens','cacheCreationInputTokens','costUSD'] if k in details} for model, details in data.get('modelUsage', {}).items()}
        if proc.returncode != 0 or data.get('is_error'):
            message = str(data.get('result', '')).lower()
            record['error_class'] = next((kind for word, kind in [('limit','limit'),('auth','auth'),('unavailable','unavailable')] if word in message), 'other_cli_error')
        else:
            ids = list(record['model_usage'])
            if not ids or any(f'claude-{args.model}-5-5' not in name for name in ids):
                record['error_class'] = 'unverified_or_mismatched_model'
            answer = data.get('result', '')
            # Successful synthetic answers only; failed result strings stay private.
            record['answer'] = answer
            fixtures = json.loads((ROOT / 'fixtures.json').read_text(encoding='utf-8'))['cases']
            record['score'] = score(answer, [case for case in fixtures if case['id'] in batch['ids']])
    except (ValueError, TypeError, AttributeError):
        record['error_class'] = 'invalid_cli_json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, ensure_ascii=True))
    if 'error_class' in record:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
