"""Shared helpers for vk-ads skill.

Env storage:
  ~/.claude/secrets/vk-ads/andrey.env            # our cabinet
  ~/.claude/secrets/vk-ads/clients/<slug>.env    # client cabinets

Each .env contains:
  VK_ADS_CLIENT_ID=
  VK_ADS_CLIENT_SECRET=
  VK_ADS_CLIENT_NAME=
  VK_ADS_ACCESS_TOKEN=          # 24h TTL
  VK_ADS_REFRESH_TOKEN=
  VK_ADS_TOKEN_EXPIRES=ISO8601  # UTC
  VK_ADS_SCOPES=                # optional, e.g. "read_ads,create_ads"
"""

import os
import io
import json
import hashlib
import mimetypes
import datetime
import urllib.request
import urllib.parse
import urllib.error
import uuid

SECRETS_DIR = os.path.expanduser('~/.claude/secrets/vk-ads')
API_BASE = 'https://ads.vk.com'
TOKEN_URL = f'{API_BASE}/api/v2/oauth2/token.json'


def env_path(client_slug):
    if client_slug == 'andrey':
        return os.path.join(SECRETS_DIR, 'andrey.env')
    return os.path.join(SECRETS_DIR, 'clients', f'{client_slug}.env')


def load_env(client_slug):
    path = env_path(client_slug)
    if not os.path.exists(path):
        raise FileNotFoundError(f'No creds for {client_slug} at {path}')
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env


def save_env(client_slug, env):
    path = env_path(client_slug)
    lines = []
    written_keys = set()
    if os.path.exists(path):
        for raw in open(path).read().splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith('#') or '=' not in stripped:
                lines.append(raw)
                continue
            k = stripped.split('=', 1)[0].strip()
            if k in env:
                lines.append(f'{k}={env[k]}')
                written_keys.add(k)
            else:
                lines.append(raw)
    for k, v in env.items():
        if k not in written_keys:
            lines.append(f'{k}={v}')
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    os.chmod(path, 0o600)


def _request_new_token(env):
    data = urllib.parse.urlencode({
        'grant_type': 'client_credentials',
        'client_id': env['VK_ADS_CLIENT_ID'],
        'client_secret': env['VK_ADS_CLIENT_SECRET'],
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get_access_token(client_slug, force_refresh=False):
    env = load_env(client_slug)
    access = env.get('VK_ADS_ACCESS_TOKEN', '')
    expires = env.get('VK_ADS_TOKEN_EXPIRES', '')
    now = datetime.datetime.utcnow()

    needs_refresh = force_refresh or not access
    if not needs_refresh and expires:
        try:
            exp_dt = datetime.datetime.fromisoformat(expires.rstrip('Z'))
            if exp_dt - now < datetime.timedelta(minutes=5):
                needs_refresh = True
        except ValueError:
            needs_refresh = True
    elif not expires:
        needs_refresh = True

    if needs_refresh:
        tok = _request_new_token(env)
        env['VK_ADS_ACCESS_TOKEN'] = tok['access_token']
        if 'refresh_token' in tok:
            env['VK_ADS_REFRESH_TOKEN'] = tok['refresh_token']
        env['VK_ADS_TOKEN_TYPE'] = tok.get('token_type', 'Bearer')
        if 'scope' in tok:
            env['VK_ADS_SCOPES'] = tok['scope']
        exp = now + datetime.timedelta(seconds=int(tok['expires_in']))
        env['VK_ADS_TOKEN_EXPIRES'] = exp.isoformat() + 'Z'
        save_env(client_slug, env)
        access = tok['access_token']

    return access


def _read_error(e):
    try:
        body = e.read().decode('utf-8')
    except Exception:
        body = ''
    return f'VK Ads API {e.code} on {e.url if hasattr(e, "url") else ""}: {body[:800]}'


def request(client_slug, method, path, params=None, body=None, files=None):
    """Universal HTTP call. body=dict → JSON. files=dict{field:(filename,bytes,mime)} → multipart."""
    token = get_access_token(client_slug)
    url = f'{API_BASE}{path}'
    if params:
        qs = urllib.parse.urlencode(params, safe=',')
        url = f'{url}?{qs}' if '?' not in url else f'{url}&{qs}'

    headers = {'Authorization': f'Bearer {token}'}
    data = None

    if files:
        boundary = f'----vkads{uuid.uuid4().hex}'
        headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        buf = io.BytesIO()

        def w(s):
            buf.write(s.encode('utf-8') if isinstance(s, str) else s)

        if body:
            for k, v in body.items():
                w(f'--{boundary}\r\n')
                w(f'Content-Disposition: form-data; name="{k}"\r\n\r\n')
                w(str(v))
                w('\r\n')
        for field, tup in files.items():
            fname, content, mime = tup
            w(f'--{boundary}\r\n')
            w(f'Content-Disposition: form-data; name="{field}"; filename="{fname}"\r\n')
            w(f'Content-Type: {mime}\r\n\r\n')
            w(content)
            w('\r\n')
        w(f'--{boundary}--\r\n')
        data = buf.getvalue()
    elif body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            if not raw:
                return {'_status': r.status}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {'_raw': raw.decode('utf-8', errors='replace')}
    except urllib.error.HTTPError as e:
        if e.code == 401:
            get_access_token(client_slug, force_refresh=True)
            token = load_env(client_slug)['VK_ADS_ACCESS_TOKEN']
            req.add_header('Authorization', f'Bearer {token}')
            try:
                with urllib.request.urlopen(req) as r:
                    raw = r.read()
                    return json.loads(raw) if raw else {'_status': r.status}
            except urllib.error.HTTPError as e2:
                raise RuntimeError(_read_error(e2)) from e2
        raise RuntimeError(_read_error(e)) from e


def api(client_slug, path, params=None):
    """Backward-compatible GET wrapper."""
    return request(client_slug, 'GET', path, params=params)


def upload_content(client_slug, file_path, kind='static'):
    """Upload a creative file. kind: static | video. Returns content dict with id/url."""
    with open(file_path, 'rb') as f:
        content = f.read()
    fname = os.path.basename(file_path)
    mime, _ = mimetypes.guess_type(fname)
    mime = mime or 'application/octet-stream'
    endpoint = f'/api/v2/content/{kind}.json'
    return request(client_slug, 'POST', endpoint, files={'file': (fname, content, mime)})


# --- audience hashing ---

def _norm_phone(s):
    digits = ''.join(ch for ch in s if ch.isdigit())
    if not digits:
        return None
    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    if len(digits) == 10:
        digits = '7' + digits
    return digits


def _norm_email(s):
    s = s.strip().lower()
    return s if '@' in s else None


def hash_audience(values, kind='phone'):
    """SHA256-hash phones or emails per VK spec. Returns list of hex digests."""
    out = []
    normaliser = _norm_phone if kind == 'phone' else _norm_email
    for v in values:
        if not v:
            continue
        n = normaliser(str(v))
        if not n:
            continue
        out.append(hashlib.sha256(n.encode('utf-8')).hexdigest())
    return out


def load_client_config(client_slug):
    path = os.path.expanduser(f'~/.claude/skills/vk-ads/clients/{client_slug}.json')
    if not os.path.exists(path):
        raise FileNotFoundError(f'No mapping config at {path}')
    with open(path) as f:
        return json.load(f)


RU_MONTHS = {
    1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
    5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
    9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь',
}


def month_name_ru(year, month, style='short26'):
    mn = RU_MONTHS[month]
    if style == 'short26':
        return f'{mn} {year % 100:02d}'
    return f'{mn} {year}'


def month_date_range(year, month):
    start = datetime.date(year, month, 1)
    if month == 12:
        end = datetime.date(year, 12, 31)
    else:
        end = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    return start.isoformat(), end.isoformat()
