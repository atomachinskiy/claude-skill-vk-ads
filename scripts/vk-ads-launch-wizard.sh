#!/usr/bin/env bash
# vk-ads-launch-wizard.sh — открывает ОТДЕЛЬНОЕ окно терминала с интерактивным
# мастером настройки. AI вызывает этот скрипт через Bash tool — у пользователя
# открывается окно (Terminal на Mac / новое PowerShell-окно на Windows / любой
# эмулятор на Linux), где он вводит client_id и client_secret от VK Ads.
#
# AI client_secret не видит — он остаётся в отдельном окне.
#
# На Windows AI должен звать vk-ads-launch-wizard.ps1 через PowerShell.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WIZARD="$SCRIPT_DIR/vk-ads-oauth-setup.sh"
[ -f "$WIZARD" ] || { echo "❌ Не найден $WIZARD"; exit 1; }

OS="$(uname -s 2>/dev/null || echo unknown)"

case "$OS" in
  Darwin)
    ESCAPED_PATH="${WIZARD//\"/\\\"}"
    /usr/bin/osascript <<EOF
tell application "Terminal"
    activate
    do script "bash \"$ESCAPED_PATH\""
end tell
EOF
    echo "✅ Открыл Terminal.app с мастером VK Ads. Перейди в новое окно."
    ;;

  Linux|WSL*)
    if command -v gnome-terminal >/dev/null 2>&1; then
      gnome-terminal -- bash -c "bash '$WIZARD'; echo; read -p 'Нажми Enter чтобы закрыть...'"
    elif command -v konsole >/dev/null 2>&1; then
      konsole -e bash -c "bash '$WIZARD'; echo; read -p 'Нажми Enter чтобы закрыть...'"
    elif command -v xterm >/dev/null 2>&1; then
      xterm -e bash -c "bash '$WIZARD'; echo; read -p 'Нажми Enter чтобы закрыть...'"
    elif command -v xfce4-terminal >/dev/null 2>&1; then
      xfce4-terminal -e "bash -c \"bash '$WIZARD'; echo; read -p 'Нажми Enter чтобы закрыть...'\""
    else
      echo "❌ Не нашёл терминал-эмулятор. Запусти руками:"
      echo "    bash \"$WIZARD\""
      exit 1
    fi
    echo "✅ Открыл терминал с мастером VK Ads."
    ;;

  MINGW*|MSYS*|CYGWIN*)
    # На Windows AI должен предпочесть vk-ads-launch-wizard.ps1 (native PS).
    # Этот fallback — для случая когда у пользователя установлен Git Bash.
    NATIVE_WIZARD="$(cygpath -w "$WIZARD" 2>/dev/null || echo "$WIZARD")"
    GIT_BASH="$(command -v bash || echo 'C:\Program Files\Git\bin\bash.exe')"
    NATIVE_BASH="$(cygpath -w "$GIT_BASH" 2>/dev/null || echo "$GIT_BASH")"
    powershell.exe -NoProfile -Command "Start-Process powershell -ArgumentList '-NoExit','-Command',\"& '$NATIVE_BASH' '$NATIVE_WIZARD'\""
    echo "✅ Открыл PowerShell-окно с мастером VK Ads (через Git Bash)."
    echo "💡 Если Git Bash не установлен — используй вместо этого скрипта:"
    echo "    powershell -ExecutionPolicy Bypass -File \"$SCRIPT_DIR/vk-ads-launch-wizard.ps1\""
    ;;

  *)
    echo "❌ Не распознал ОС ($OS). Запусти мастер руками:"
    echo "    bash \"$WIZARD\""
    exit 1
    ;;
esac
