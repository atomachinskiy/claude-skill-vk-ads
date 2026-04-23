#!/usr/bin/env python3
"""Create VK Ads objects from a JSON template.

Usage:
  create.py <slug> <type> --body body.json [--dry-run]

Types and their endpoints:
  campaign       → POST /api/v2/ad_plans.json
  adgroup        → POST /api/v2/ad_groups.json
  banner         → POST /api/v2/banners.json
  users-list     → POST /api/v2/remarketing/users_lists.json
  segment        → POST /api/v2/remarketing/segments.json

The --body JSON is sent as-is. See templates/ for starter bodies per type.
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from common import request  # noqa: E402

TYPE_TO_PATH = {
    'campaign':   '/api/v2/ad_plans.json',
    'adgroup':    '/api/v2/ad_groups.json',
    'banner':     '/api/v2/banners.json',
    'users-list': '/api/v2/remarketing/users_lists.json',
    'segment':    '/api/v2/remarketing/segments.json',
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('type', choices=sorted(TYPE_TO_PATH))
    ap.add_argument('--body', required=True)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    with open(args.body) as f:
        body = json.load(f)
    path = TYPE_TO_PATH[args.type]

    if args.dry_run:
        print(f'DRY-RUN: POST {path}')
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return

    out = request(args.slug, 'POST', path, body=body)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
