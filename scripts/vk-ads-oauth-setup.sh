#!/usr/bin/env bash
# vk-ads-oauth-setup.sh — интерактивный мастер первичной настройки.
# Запускается в ОТДЕЛЬНОМ окне терминала через vk-ads-launch-wizard.sh,
# чтобы client_secret не попал в transcript AI.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECRETS_DIR="$HOME/.claude/secrets/vk-ads"
ENV_FILE="$SECRETS_DIR/clients/self.env"
VK_BASE="${VK_ADS_BASE:-https://ads.vk.com}"
TOKEN_URL="$VK_BASE/api/v2/oauth2/token.json"

C_RESET="\033[0m"
C_CYAN="\033[1;36m"
C_GREEN="\033[1;32m"
C_YELLOW="\033[1;33m"
C_RED="\033[1;31m"

die() { echo -e "${C_RED}[!] $*${C_RESET}" >&2; read -r -p "Enter чтобы закрыть… " _; exit 1; }

echo -e "${C_CYAN}═══════════════════════════════════════════════════════════════${C_RESET}"
echo -e "${C_CYAN}  VK Ads (ads.vk.com) — настройка${C_RESET}"
echo -e "${C_CYAN}═══════════════════════════════════════════════════════════════${C_RESET}"
echo ""

command -v jq   >/dev/null 2>&1 || die "Не найден jq.   macOS: brew install jq | Linux: sudo apt install jq"
command -v curl >/dev/null 2>&1 || die "Не найден curl"

mkdir -p "$SECRETS_DIR/clients"
chmod 700 "$SECRETS_DIR" 2>/dev/null || true

# Если .env существует с заполненными client_id/secret — спросить переиспользовать
USE_EXISTING_ENV=0
if [ -f "$ENV_FILE" ] \
   && grep -q '^VK_ADS_CLIENT_ID=..' "$ENV_FILE" 2>/dev/null \
   && grep -q '^VK_ADS_CLIENT_SECRET=..' "$ENV_FILE" 2>/dev/null; then
  echo -e "${C_GREEN}[✓]${C_RESET} Найден заполненный $ENV_FILE"
  read -r -p "Использовать существующие client_id/client_secret? [Y/n] " ans
  case "$ans" in
    n|N|no|No) USE_EXISTING_ENV=0 ;;
    *) USE_EXISTING_ENV=1 ;;
  esac
fi

if [ "$USE_EXISTING_ENV" = "0" ]; then
  echo ""
  echo -e "${C_YELLOW}Где взять значения:${C_RESET}"
  echo "  ads.vk.com → Профиль → Доступ к API → Запросить доступ к API"
  echo "  (после одобрения VK сгенерирует client_id и client_secret)"
  echo ""

  read -r -p "client_id: " VK_ADS_CLIENT_ID
  [ -n "$VK_ADS_CLIENT_ID" ] || die "client_id пустой"

  read -r -s -p "client_secret (вводится скрыто): " VK_ADS_CLIENT_SECRET; echo
  [ -n "$VK_ADS_CLIENT_SECRET" ] || die "client_secret пустой"

  read -r -p "Имя кабинета (любое, для себя — например, agency-msk): " VK_ADS_CLIENT_NAME
  [ -n "$VK_ADS_CLIENT_NAME" ] || VK_ADS_CLIENT_NAME="self"

  NOW="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
  cat > "$ENV_FILE" <<EOF
# VK Ads (ads.vk.com) credentials
# Сгенерировано $NOW
VK_ADS_CLIENT_ID=$VK_ADS_CLIENT_ID
VK_ADS_CLIENT_SECRET=$VK_ADS_CLIENT_SECRET
VK_ADS_CLIENT_NAME=$VK_ADS_CLIENT_NAME
VK_ADS_ISSUED_AT=$NOW
EOF
  chmod 600 "$ENV_FILE"
  echo -e "${C_GREEN}[✓]${C_RESET} Сохранил в $ENV_FILE (chmod 600)"
else
  # shellcheck disable=SC1090
  . "$ENV_FILE"
fi

echo ""
echo -e "${C_YELLOW}Получаю access/refresh-токены через client_credentials…${C_RESET}"
RESP="$(curl -sS -w '\n__HTTP_CODE__%{http_code}' -X POST "$TOKEN_URL" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "grant_type=client_credentials" \
  --data-urlencode "client_id=$VK_ADS_CLIENT_ID" \
  --data-urlencode "client_secret=$VK_ADS_CLIENT_SECRET")"
HTTP_CODE="$(printf '%s' "$RESP" | tail -n1 | sed 's/^.*__HTTP_CODE__//')"
BODY="$(printf '%s' "$RESP" | sed '$d')"

if [ "$HTTP_CODE" != "200" ]; then
  echo -e "${C_RED}[!] HTTP $HTTP_CODE${C_RESET}"
  echo "$BODY" | head -c 400
  echo ""
  die "Не удалось получить токены. Проверь client_id/client_secret в $ENV_FILE и перезапусти мастер."
fi

ACCESS="$(printf '%s' "$BODY" | jq -r '.access_token // empty')"
REFRESH="$(printf '%s' "$BODY" | jq -r '.refresh_token // empty')"
TTYPE="$(printf '%s' "$BODY" | jq -r '.token_type // "Bearer"')"
EXPIRES_IN="$(printf '%s' "$BODY" | jq -r '.expires_in // 86400')"
SCOPES="$(printf '%s' "$BODY" | jq -r '.scope // empty')"
[ -n "$ACCESS" ] || die "В ответе нет access_token: $BODY"

# Дата истечения с запасом 5 минут
EXP_ISO="$(python3 -c "import datetime; print((datetime.datetime.utcnow()+datetime.timedelta(seconds=$EXPIRES_IN-300)).isoformat()+'Z')" 2>/dev/null \
  || date -u -d "+$((EXPIRES_IN-300)) seconds" +'%Y-%m-%dT%H:%M:%SZ' 2>/dev/null \
  || date -u -v+${EXPIRES_IN}S +'%Y-%m-%dT%H:%M:%SZ')"

# Дописываем токены в .env поверх старых значений
export ACCESS_TOKEN="$ACCESS" REFRESH_TOKEN="$REFRESH" TTYPE_VAL="$TTYPE" EXP_ISO_VAL="$EXP_ISO" SCOPES_VAL="$SCOPES"
python3 - "$ENV_FILE" <<'PY'
import os, sys
path = sys.argv[1]
updates = {
    'VK_ADS_ACCESS_TOKEN': os.environ['ACCESS_TOKEN'],
    'VK_ADS_REFRESH_TOKEN': os.environ['REFRESH_TOKEN'],
    'VK_ADS_TOKEN_TYPE': os.environ['TTYPE_VAL'],
    'VK_ADS_TOKEN_EXPIRES': os.environ['EXP_ISO_VAL'],
    'VK_ADS_SCOPES': os.environ['SCOPES_VAL'],
}
lines = []
seen = set()
if os.path.exists(path):
    for raw in open(path).read().splitlines():
        s = raw.strip()
        if not s or s.startswith('#') or '=' not in s:
            lines.append(raw); continue
        k = s.split('=', 1)[0].strip()
        if k in updates:
            lines.append(f"{k}={updates[k]}")
            seen.add(k)
        else:
            lines.append(raw)
for k, v in updates.items():
    if k not in seen:
        lines.append(f"{k}={v}")
with open(path, 'w') as f:
    f.write('\n'.join(lines) + '\n')
os.chmod(path, 0o600)
PY

echo -e "${C_GREEN}[✓]${C_RESET} Токены сохранены (access живёт ${EXPIRES_IN}s, обновится автоматически)"

echo ""
echo -e "${C_YELLOW}Проверяю кабинет…${C_RESET}"
USER_INFO="$(curl -sS -H "Authorization: Bearer $ACCESS" -H 'Accept: application/json' \
  "$VK_BASE/api/v2/user.json")"
USER_ID="$(printf '%s' "$USER_INFO" | jq -r '.id // empty')"
USER_NAME="$(printf '%s' "$USER_INFO" | jq -r '.username // .first_name // empty')"
USER_TYPE="$(printf '%s' "$USER_INFO" | jq -r '.type // empty')"
USER_STATUS="$(printf '%s' "$USER_INFO" | jq -r '.status // empty')"

PLANS="$(curl -sS -H "Authorization: Bearer $ACCESS" -H 'Accept: application/json' \
  "$VK_BASE/api/v2/ad_plans.json?limit=200&fields=id,status")"
PLANS_TOTAL="$(printf '%s' "$PLANS" | jq -r '.count // 0')"
PLANS_ACTIVE="$(printf '%s' "$PLANS" | jq -r '[.items[]? | select(.status=="active")] | length // 0')"

echo ""
echo -e "${C_GREEN}═══════════════════════════════════════════════════════════════${C_RESET}"
echo -e "${C_GREEN}  ✅ VK Ads настроен и работает${C_RESET}"
echo -e "${C_GREEN}═══════════════════════════════════════════════════════════════${C_RESET}"
echo ""
echo "  Кабинет:        $USER_NAME  (id=$USER_ID, type=$USER_TYPE, status=$USER_STATUS)"
echo "  Кампаний всего: $PLANS_TOTAL"
echo "  Активных:       $PLANS_ACTIVE"
echo ""
echo "  Конфиг + токены: $ENV_FILE"
echo ""
echo "Дальше в чате с Клодом можно спрашивать:"
echo "  • «Заполни отчёт по моему VK-кабинету за месяц»"
echo "  • «Покажи активные кампании и остатки бюджета»"
echo "  • «Сравни CPM по группам объявлений»"
echo "  • «Сколько лидов получили за последние 30 дней»"
echo ""
read -r -p "Готово. Нажми Enter чтобы закрыть это окно… " _
