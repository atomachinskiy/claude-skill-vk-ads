#!/usr/bin/env python3
"""Manage existing VK Ads objects: edit, status change, delete.

Usage:
  manage.py <slug> <type> <id> edit --body patch.json     # POST /{resource}/{id}.json
  manage.py <slug> <type> <id> status <active|blocked|deleted>
  manage.py <slug> <type> <id> delete                      # DELETE /{resource}/{id}.json

Types: campaign|adgroup|banner|users-list|segment

Status maps:
  active   → {"status": "active"}          # unpause / start
  blocked  → {"status": "blocked"}         # pause
  deleted  → {"status": "deleted"}         # soft-delete / archive

Supports comma-separated IDs for bulk ops.
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from common import request  # noqa: E402

TYPE_TO_PATH = {
    'campaign':   '/api/v2/ad_plans',
    'adgroup':    '/api/v2/ad_groups',
    'banner':     '/api/v2/banners',
    'users-list': '/api/v2/remarketing/users_lists',
    'segment':    '/api/v2/remarketing/segments',
}

STATUSES = {'active', 'blocked', 'deleted'}


def ids_from_arg(s):
    return [x.strip() for x in s.split(',') if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('type', choices=sorted(TYPE_TO_PATH))
    ap.add_argument('id', help='id or comma-separated ids')
    ap.add_argument('action', choices=['edit', 'status', 'delete'])
    ap.add_argument('value', nargs='?', help='status value for "status" action')
    ap.add_argument('--body', help='patch JSON file for "edit"')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    base = TYPE_TO_PATH[args.type]
    results = []

    for oid in ids_from_arg(args.id):
        path = f'{base}/{oid}.json'
        if args.action == 'delete':
            method, body = 'DELETE', None
        elif args.action == 'status':
            if args.value not in STATUSES:
                raise SystemExit(f'status must be one of {sorted(STATUSES)}')
            method, body = 'POST', {'status': args.value}
        else:  # edit
            if not args.body:
                raise SystemExit('edit requires --body')
            with open(args.body) as f:
                body = json.load(f)
            method = 'POST'

        if args.dry_run:
            print(f'DRY-RUN: {method} {path}  body={body}')
            continue
        results.append({'id': oid, 'response': request(args.slug, method, path, body=body)})

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
