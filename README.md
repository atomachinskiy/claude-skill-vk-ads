# vk-ads — Claude Code skill для VK Реклама API

Скилл для [Claude Code](https://docs.claude.com/en/docs/claude-code), который превращает Claude в сеньор-таргетолога ВК. Закрывает полный цикл рекламного кабинета через [VK Ads API](https://ads.vk.com/help/api): чтение, запуск, оптимизацию, отчётность и ОРД-маркировку для агентств.

## Что умеет

**Чтение и аналитика**
- Статистика v2/v3, прогноз охвата, аудиторные инсайты
- Авто-заполнение месячных отчётов в Google Sheets
- Выгрузка лидов из лид-форм
- ТОП объявлений по CTR / CR / ROMI

**Запуск и создание**
- Кампании, группы, баннеры по шаблонам
- Загрузка аудиторий ремаркетинга (телефоны, email — с SHA-256)
- Look-alike сегменты
- Лид-формы и опросы

**Управление**
- Массовые операции (до 200 объектов/запрос)
- Модерация, бюджеты, ставки
- Замена креативов, остановка/возобновление
- Удаление кампаний оптом

**ОРД для агентств**
- Полный цикл маркировки рекламы для агентских кабинетов
- Акты и отчётность

Скилл сделан с упором на проактивные подсказки — не просто выполняет команду, а подсказывает что ещё можно сделать. Большинство таргетологов ВК не используют и половины возможностей API.

## Установка

```bash
git clone --depth 1 https://github.com/atomachinskiy/claude-skill-vk-ads.git ~/.claude/skills/vk-ads
```

После клона скилл автоматически подхватится Claude Code при запуске в любой папке.

## Требования

- Python 3.11+
- Claude Code установлен и работает
- VK Ads OAuth-приложение (`client_id` + `client_secret`) — запросить у клиента или получить на ads.vk.com
- (Опционально) Google Sheets API credentials — для авто-заполнения отчётов

## Setup секретов

Креды живут отдельно от скилла, в `~/.claude/secrets/vk-ads/`. Никогда не попадают в git.

```bash
mkdir -p ~/.claude/secrets/vk-ads/clients
chmod 700 ~/.claude/secrets/vk-ads

cat > ~/.claude/secrets/vk-ads/clients/<slug>.env <<'EOF'
VK_ADS_CLIENT_ID=...
VK_ADS_CLIENT_SECRET=...
VK_ADS_CLIENT_NAME=Имя клиента (ниша)
VK_ADS_ISSUED_AT=2026-04-01
EOF

chmod 600 ~/.claude/secrets/vk-ads/clients/<slug>.env
```

Где `<slug>` — короткий идентификатор клиента (например `acme`).

Smoke-тест что токен живой:

```bash
python3 ~/.claude/skills/vk-ads/scripts/cli.py <slug> GET /api/v2/ad_plans.json --param limit=5
```

## Конфиг клиента (для отчётов)

Чтобы скилл знал, в какую Google-таблицу класть отчёт по клиенту, создай `~/.claude/skills/vk-ads/clients/<slug>.json` по шаблону `templates/client-template.json`. Маппит строки таблицы → ad_group_id, формулы итогов и тд.

## Использование

Просто пиши Claude естественным языком в своём проекте:

- «Заполни отчёт acme за апрель»
- «Покажи активные кампании acme и остатки бюджета»
- «Запусти ретаргет на ушедших из корзины — бюджет 30К/мес»
- «Загрузи базу телефонов из contacts.txt как аудиторию для acme»
- «Выгрузи лиды из формы 12345 за прошлый месяц»
- «Подсчитай охват если возьму бюджет 50К на ЦА женщины 25-45 Москва»

Скилл сам разберётся с API, токенами, форматами и подскажет следующий шаг.

## Структура

```
SKILL.md                — главный файл скилла (~660 строк инструкций для Claude)
references/             — справочники по разделам API
  endpoints-catalog.md  — полный реестр эндпоинтов и объектов
  audiences.md          — аудитории, ремаркетинг, LAL
  auth.md               — OAuth, refresh-токены, Agency Client Credentials
  creatives.md          — баннеры, форматы, креативы
  lead-forms.md         — лид-формы, выгрузка лидов
  mass-actions.md       — массовые операции
  objects-catalog.md    — схемы объектов API
  ord.md                — ОРД для агентств
  projections.md        — прогноз охвата
  recipes.md            — типовые рецепты задач
  statistics.md         — Statistics API v2/v3
  targetings.md         — таргетинги
scripts/                — Python-скрипты, которые вызывает Claude
  common.py             — OAuth refresh, request(), shared utils
  cli.py                — универсальный API-вызов
  create.py             — создание объектов из шаблонов
  manage.py             — управление (старт/стоп/бюджет)
  upload-audience.py    — загрузка аудиторий с SHA-256
  fill-monthly-report.py — заполнение Google Sheets отчёта
templates/              — JSON-шаблоны (campaign, adgroup, banner, segment, audience)
clients/                — конфиги клиентов (gitignored, кроме .gitkeep)
```

## Источник документации

References — авторская переработка офиц. доки VK Ads под AI-friendly справочник. За полной документацией см.: https://ads.vk.com/help/api

## Лицензия

MIT — см. [LICENSE](LICENSE).

## Автор

Andrey Tomachinskiy — таргетолог, перформанс-маркетолог, AI-операционник.
