"""Exact synthetic-case scorer. No model calls or credentials."""
import json


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate key: {key}')
        result[key] = value
    return result


def score(text, cases):
    ids = [case['id'] for case in cases]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError('oracle needs nonempty unique case IDs')
    expected = {case['id']: case['answer'] for case in cases}
    try:
        actual = json.loads(text, object_pairs_hook=unique_object)
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ValueError('response key set differs from oracle')
        if not all(isinstance(value, str) for value in actual.values()):
            raise ValueError('answer values must be strings')
    except (ValueError, TypeError) as error:
        return {'correct': 0, 'total': len(ids), 'pass': False, 'invalid': str(error)}
    matches = {key: actual[key] == value for key, value in expected.items()}
    return {'correct': sum(matches.values()), 'total': len(ids),
            'pass': all(matches.values()), 'matches': matches}
