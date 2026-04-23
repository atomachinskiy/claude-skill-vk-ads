#!/usr/bin/env python3
"""Upload a remarketing users_list to VK Ads.

Usage:
  upload-audience.py <slug> <name> <file> [--kind phone|email|mixed] [--already-hashed]

File format: one value per line (phone or email). Empty lines and '#'-comments skipped.
Normalises phones to digits (7XXXXXXXXXX), emails to lowercase, then SHA256-hashes
unless --already-hashed is passed.

Creates /api/v2/remarketing/users_lists.json with type=1 (hashed contacts).
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from common import request, hash_audience  # noqa: E402


def read_values(path):
    out = []
    with open(path) as f:
        for line in f:
            v = line.strip()
            if not v or v.startswith('#'):
                continue
            out.append(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('name', help='audience name shown in cabinet')
    ap.add_argument('file')
    ap.add_argument('--kind', default='phone', choices=['phone', 'email', 'mixed'])
    ap.add_argument('--already-hashed', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    raw = read_values(args.file)
    if args.already_hashed:
        items = [v.lower() for v in raw if len(v) == 64]
    elif args.kind == 'mixed':
        phones = hash_audience([v for v in raw if any(c.isdigit() for c in v) and '@' not in v], 'phone')
        emails = hash_audience([v for v in raw if '@' in v], 'email')
        items = phones + emails
    else:
        items = hash_audience(raw, args.kind)

    if not items:
        raise SystemExit(f'No valid entries found in {args.file}')

    body = {
        'name': args.name,
        'type': 1,                # hashed contacts list
        'users': ','.join(items), # comma-separated hex digests
    }

    if args.dry_run:
        print(f'DRY-RUN: POST /api/v2/remarketing/users_lists.json')
        print(f'name={args.name}  entries={len(items)} (first hash: {items[0][:12]}...)')
        return

    out = request(args.slug, 'POST', '/api/v2/remarketing/users_lists.json', body=body)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
