"""Deterministic field-aware chunking; never index evaluation references."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def chunk_documents(documents, max_chars=800, overlap_chars=100):
    if max_chars < 100 or not 0 <= overlap_chars < max_chars:
        raise ValueError('Require max_chars >= 100 and 0 <= overlap < max_chars')
    chunks, seen = [], set()
    for doc in documents:
        identity, text = doc['doc_id'], doc['text']
        if identity in seen or not identity or not text.strip():
            raise ValueError('Duplicate/empty document')
        seen.add(identity)
        start, index = 0, 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            if end < len(text):
                boundary = text.rfind('\n', start + max_chars // 2, end)
                if boundary != -1:
                    end = boundary + 1
                else:
                    boundary = text.rfind(' ', start + max_chars // 2, end)
                    if boundary != -1:
                        end = boundary + 1
            chunks.append({'chunk_id': f'{identity}::c{index:03d}', 'doc_id': identity,
                           'text': text[start:end], 'start_char': start, 'end_char': end,
                           'source_url': doc['source_url']})
            if end == len(text):
                break
            next_start = max(start + 1, end - overlap_chars)
            # Avoid starting in the middle of a word; retain positive progress.
            while next_start < end and next_start > 0 and not text[next_start-1].isspace():
                next_start += 1
            start, index = next_start, index + 1
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--max-chars', type=int, default=800)
    parser.add_argument('--overlap-chars', type=int, default=100)
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error('Use a new/empty output directory')
    source = ROOT / 'corpus/documents.jsonl'
    docs = [json.loads(line) for line in source.read_text(encoding='utf-8').splitlines()]
    chunks = chunk_documents(docs, args.max_chars, args.overlap_chars)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data = ''.join(json.dumps(c, ensure_ascii=False, sort_keys=True)+'\n' for c in chunks).encode('utf-8')
    (args.output_dir / 'chunks.jsonl').write_bytes(data)
    stats = {'documents': len(docs), 'chunks': len(chunks), 'units': 'characters_not_tokens',
             'max_chars': args.max_chars, 'overlap_chars': args.overlap_chars,
             'corpus_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
             'chunks_sha256': hashlib.sha256(data).hexdigest(),
             'status': 'chunking_only_not_embedding_index'}
    (args.output_dir / 'manifest.json').write_bytes((json.dumps(stats, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
