#!/usr/bin/env python3
"""Universal CLI for ads.vk.com.

Usage:
  cli.py <slug> <METHOD> <path> [--param k=v ...] [--body body.json | --body-inline '{...}']
  cli.py <slug> upload-content <file> [--kind static|video]

Examples:
  cli.py andrey GET /api/v2/ad_plans.json --param limit=50 --param fields=id,name,status
  cli.py andrey POST /api/v2/ad_plans.json --body plan.json
  cli.py andrey upload-content ./creative.jpg --kind static
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from common import request, upload_content  # noqa: E402


def parse_kv_list(items):
    out = {}
    for item in items or []:
        if '=' not in item:
            raise SystemExit(f'--param expects k=v, got: {item}')
        k, v = item.split('=', 1)
        out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('method')
    ap.add_argument('path_or_file', nargs='?')
    ap.add_argument('--param', action='append', default=[])
    ap.add_argument('--body', help='path to JSON file')
    ap.add_argument('--body-inline', help='inline JSON string')
    ap.add_argument('--kind', default='static', help='for upload-content')
    ap.add_argument('--pretty', action='store_true')
    args = ap.parse_args()

    if args.method == 'upload-content':
        if not args.path_or_file:
            raise SystemExit('upload-content requires <file>')
        out = upload_content(args.slug, args.path_or_file, kind=args.kind)
    else:
        if not args.path_or_file:
            raise SystemExit('<path> required')
        params = parse_kv_list(args.param)
        body = None
        if args.body:
            with open(args.body) as f:
                body = json.load(f)
        elif args.body_inline:
            body = json.loads(args.body_inline)
        out = request(args.slug, args.method, args.path_or_file, params=params, body=body)

    indent = 2 if args.pretty else None
    print(json.dumps(out, ensure_ascii=False, indent=indent))


if __name__ == '__main__':
    main()
