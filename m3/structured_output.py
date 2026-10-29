"""Strict JSON with optional Markdown fence; never execute model-generated text."""
import json
import re


def parse_object(raw):
    if not isinstance(raw, str) or len(raw) > 20000:
        raise ValueError('Invalid or oversized JSON response')
    text = raw.strip()
    match = re.fullmatch(r'```(?:json)?\s*\n?(.*?)\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('Non-finite JSON value: ' + value)

    obj = json.loads(text, object_pairs_hook=unique, parse_constant=invalid_constant)
    if not isinstance(obj, dict):
        raise ValueError('Expected one JSON object')
    return obj
