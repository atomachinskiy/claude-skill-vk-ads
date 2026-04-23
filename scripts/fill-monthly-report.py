#!/usr/bin/env python3
"""Fill a monthly VK Ads report in client's Google Sheet.

Usage:
  fill-monthly-report.py <client-slug> <YYYY-MM> [--create-if-missing] [--dry-run]

Example:
  fill-monthly-report.py acme 2026-04
  fill-monthly-report.py acme 2026-04 --create-if-missing

Config file:  ~/.claude/skills/vk-ads/clients/<slug>.json
Creds:        ~/.claude/secrets/vk-ads/clients/<slug>.env
"""

import sys
import os
import argparse
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (
    api, load_client_config, month_name_ru, month_date_range,
)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SHEETS_TOKEN = os.path.expanduser(
    '~/.claude/skills/google-sheets-skill/tokens/token_default.json'
)


def get_sheets_service():
    creds = Credentials.from_authorized_user_file(SHEETS_TOKEN)
    return build('sheets', 'v4', credentials=creds)


def find_sheet(service, spreadsheet_id, title):
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for s in meta['sheets']:
        if s['properties']['title'] == title:
            return s['properties']['sheetId']
    return None


def duplicate_sheet(service, spreadsheet_id, source_sheet_id, new_title, insert_index=None):
    body = {'requests': [{
        'duplicateSheet': {
            'sourceSheetId': source_sheet_id,
            'newSheetName': new_title,
            **({'insertSheetIndex': insert_index} if insert_index is not None else {}),
        }
    }]}
    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()
    return resp['replies'][0]['duplicateSheet']['properties']['sheetId']


def sheet_index(service, spreadsheet_id, sheet_id):
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for i, s in enumerate(meta['sheets']):
        if s['properties']['sheetId'] == sheet_id:
            return i
    return None


def fetch_stats(client_slug, ad_group_ids, date_from, date_to):
    ids = ','.join(str(x) for x in ad_group_ids)
    resp = api(
        client_slug,
        '/api/v3/statistics/ad_groups/day.json',
        {
            'id': ids,
            'date_from': date_from,
            'date_to': date_to,
            'metrics': 'base,events',
        },
    )
    stats = {}
    for item in resp.get('items', []):
        tot = item.get('total', {}).get('base', {}) or {}
        vk = tot.get('vk', {}) or {}
        stats[item['id']] = {
            'spent': float(tot.get('spent') or 0),
            'shows': int(tot.get('shows') or 0),
            'clicks': int(tot.get('clicks') or 0),
            'goals': int(vk.get('goals') or 0),
        }
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('client', help='Client slug (e.g. acme)')
    ap.add_argument('month', help='YYYY-MM, e.g. 2026-04')
    ap.add_argument('--create-if-missing', action='store_true',
                    help='Duplicate template sheet if target month tab does not exist')
    ap.add_argument('--dry-run', action='store_true',
                    help='Print actions but do not write to Sheets')
    args = ap.parse_args()

    year, month = map(int, args.month.split('-'))
    date_from, date_to = month_date_range(year, month)

    config = load_client_config(args.client)
    spreadsheet_id = config['spreadsheet_id']
    sheet_name_style = config.get('sheet_name_style', 'short26')
    target_name = month_name_ru(year, month, sheet_name_style)

    print(f'Client:     {config.get("name", args.client)}')
    print(f'Spreadsheet: {spreadsheet_id}')
    print(f'Target tab: {target_name}')
    print(f'Period:     {date_from} → {date_to}')

    service = get_sheets_service()
    sheet_id = find_sheet(service, spreadsheet_id, target_name)

    if sheet_id is None:
        if not args.create_if_missing:
            sys.exit(
                f'❌ Tab "{target_name}" not found. '
                f'Use --create-if-missing to duplicate template.'
            )
        template_name = config.get('template_sheet_name')
        if not template_name:
            sys.exit('❌ No template_sheet_name in config')
        template_id = find_sheet(service, spreadsheet_id, template_name)
        if template_id is None:
            sys.exit(f'❌ Template "{template_name}" not found')
        template_idx = sheet_index(service, spreadsheet_id, template_id)
        if args.dry_run:
            print(f'[dry-run] Would duplicate "{template_name}" → "{target_name}"')
            return
        sheet_id = duplicate_sheet(
            service, spreadsheet_id, template_id, target_name,
            insert_index=(template_idx + 1) if template_idx is not None else None,
        )
        print(f'✅ Created tab "{target_name}" (duplicate of "{template_name}")')

        # Clear fields that carry template values
        clear_cells = config.get('clear_on_create', [])
        if clear_cells:
            ranges = [f"'{target_name}'!{r}" for r in clear_cells]
            service.spreadsheets().values().batchClear(
                spreadsheetId=spreadsheet_id, body={'ranges': ranges}
            ).execute()
            print(f'🧹 Cleared {len(ranges)} template ranges')

    # Pull stats
    row_map = {int(k): v for k, v in config['row_to_ad_group'].items()}
    stats = fetch_stats(args.client, list(row_map.values()), date_from, date_to)

    # Build updates
    cells = config['cells']  # {spent, shows, clicks, goals} → col letters
    updates = []
    print(f'\n{"Row":<4} {"Group":<12} {"Spent":>10} {"Shows":>8} {"Clicks":>8} {"Goals":>6}')
    for row, gid in row_map.items():
        s = stats.get(gid, {'spent': 0, 'shows': 0, 'clicks': 0, 'goals': 0})
        print(f'R{row:<3} {gid:<12} {s["spent"]:>10.2f} {s["shows"]:>8} {s["clicks"]:>8} {s["goals"]:>6}')
        updates.append({
            'range': f"'{target_name}'!{cells['spent']}{row}:{cells['clicks']}{row}",
            'values': [[s['spent'], s['shows'], s['clicks']]],
        })
        updates.append({
            'range': f"'{target_name}'!{cells['goals']}{row}",
            'values': [[s['goals']]],
        })

    # ИТОГО formulas
    for total in config.get('totals', []):
        trow = total['row']
        s, e = total['range']
        for col in (cells['spent'], cells['shows'], cells['clicks']):
            updates.append({
                'range': f"'{target_name}'!{col}{trow}",
                'values': [[f'=SUM({col}{s}:{col}{e})']],
            })
        updates.append({
            'range': f"'{target_name}'!{cells['goals']}{trow}",
            'values': [[f'=SUM({cells["goals"]}{s}:{cells["goals"]}{e})']],
        })

    # Custom formula rows (e.g. grand ИТОГО R24 = C9+C15+C22)
    for formula in config.get('custom_formulas', []):
        row = formula['row']
        for col_key, expr in formula['exprs'].items():
            col = cells[col_key]
            updates.append({
                'range': f"'{target_name}'!{col}{row}",
                'values': [[expr]],
            })

    if args.dry_run:
        print(f'\n[dry-run] Would write {len(updates)} ranges')
        return

    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'valueInputOption': 'USER_ENTERED', 'data': updates},
    ).execute()
    print(f'\n✅ Updated {result.get("totalUpdatedCells", 0)} cells')
    print(f'🔗 https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}')


if __name__ == '__main__':
    main()
