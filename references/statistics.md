# VK Ads — Статистика

## Два поколения API

### v2 — простой срез
`GET /api/v2/statistics/{banners|ad_groups|ad_plans|users}/{day|summary}.json`

- **Лимиты:** макс 200 объектов в запросе, макс 366 дней
- **Без пагинации** — всё одним ответом
- Подходит: быстрый срез, мало объектов, дашборды
- Не подходит: ETL-выгрузка, большие периоды

### v3 — промышленный с пагинацией
`GET /api/v3/statistics/{banners|ad_groups|ad_plans|users}/day.json`

- **Пагинация курсором**: параметр `cursor`, `limit` до 250
- Подходит: выгрузка за год, 500+ объектов, ETL
- Ответ содержит `next_cursor` если есть ещё данные

## Уровни среза (типы объектов)

| URL | Срез по |
|---|---|
| `/banners/` | Отдельные баннеры |
| `/ad_groups/` | Группы объявлений |
| `/ad_plans/` | Кампании |
| `/users/` | Весь кабинет (только для users scope) |

## Виды срезов (v2 only)

- `/day.json` — по дням в периоде (ряд точек)
- `/summary.json` — итог за период (одна точка)

v3 — только `/day.json` (summary собирается клиентом).

## Параметры запроса

```
id=1001,1002,1003          # IDs объектов (comma-sep)
date_from=2026-04-01       # начало периода (YYYY-MM-DD)
date_to=2026-04-30         # конец периода (YYYY-MM-DD)
metrics=base,events        # набор метрик (см. ниже)
cursor=<cursor>            # v3 только, пагинация
limit=250                  # v3 только (до 250)
```

## Метрик-сеты (`metrics` параметр)

Нельзя запросить «всё сразу» — надо выбирать наборы. Комбинируй через запятую.

| Набор | Что внутри | Когда использовать |
|---|---|---|
| `base` | impressions, clicks, spent, ctr, cpm, cpc | Почти всегда (базовый скелет отчёта) |
| `events` | Конверсии по целям счётчика: goal_<id>_value, goal_<id>_cost | Счётчик Top@Mail.ru с настроенными целями |
| `uniques` | reach, frequency, impressions_unique, clicks_unique | Охватные кампании, brand-lift |
| `video` | video_views, video_view_25/50/75/100, vtr | Видео-креативы |
| `uniques_video` | Unique video-смотры по процентам | Брендовое видео |
| `carousel` | carousel_click_N, carousel_click_any | Carousel формат |
| `tps` | slide_show, slide_complete, time_per_slide | Stories / Clips |
| `playable` | playable_interactions, playable_completions | Playable ads (мобилки) |
| `romi` | revenue, romi, roas | E-com с атрибуцией покупок |
| `ad_offers` | Product-level stats (per товар) | Динамический ретаргет каталога |
| `social_network` | likes, reposts, group_joins, comments | Промо сообществ VK |
| `custom_event` | Пользовательские события | Кастомная атрибуция |

## Примеры

### v2: стата по 50 группам за апрель
```bash
cli.py andrey GET /api/v2/statistics/ad_groups/day.json \
  --param id=1001,1002,...,1050 \
  --param date_from=2026-04-01 \
  --param date_to=2026-04-30 \
  --param metrics=base,events,uniques
```

### v3: полная выгрузка по кабинету (постранично)
```bash
# первая страница
cli.py andrey GET /api/v3/statistics/ad_groups/day.json \
  --param date_from=2026-01-01 \
  --param date_to=2026-04-21 \
  --param metrics=base,events \
  --param limit=250

# получил next_cursor=XYZ → следующая
cli.py andrey GET /api/v3/statistics/ad_groups/day.json \
  --param date_from=2026-01-01 --param date_to=2026-04-21 \
  --param metrics=base,events --param limit=250 \
  --param cursor=XYZ

# повторять пока next_cursor не пуст
```

### Прогноз охвата (отдельный эндпоинт)
```bash
cli.py andrey POST /api/v2/ad_plans/<ad_plan_id>/projection.json \
  --body /tmp/projection-body.json
```

## Goals stats (конверсии по целям)

В наборе `events` каждая цель даёт:
- `goal_<id>` — количество достижений
- `goal_<id>_value` — суммарная ценность (если у цели есть цена)
- `goal_<id>_cost` — стоимость достижения (cpa per goal)

Для подсчёта CPA используй: `spent / goal_<id>`.

## Offline conversions (оффлайн-конверсии)

Если загружены через `remarketing_offline_goals.json`, они попадают в `events` с префиксом `offline_goal_<id>`.

## InApp Events stats (мобилки)

Для мобильных приложений доступны inapp_event метрики через `custom_event` набор. Подключаются через `remarketing_inapp_events`.

## Fast stats (быстрый срез сегодня)

Для «сегодня не доcчиталось» используй **v3 summary** — он даёт быстрые данные (за последние несколько часов задержка ~30 мин). v2 для «сегодня» может сильно отставать.

## Ограничения и анти-паттерны

- **v2 + >200 объектов** → 400 или обрезание. Перейди на v3.
- **Период >366 дней** → 400. Дели на годовые куски.
- **Все метрики одним запросом** → физически нельзя, выбирай релевантные.
- **`sorting` в stats** → не все поля сортируемы, документацию по v3 читать внимательно.
- **Сегодняшние данные** — задержка 1-3 часа, не паникуй.
- **Статистика мертвых объектов** — если объект status=deleted, статистика всё равно возвращается за период когда он был активен.

## Типовые рецепты

### Отчёт «за месяц» для клиента
```
1. cli.py GET /api/v2/ad_plans.json _status=active → список IDs
2. cli.py GET /api/v3/statistics/ad_plans/day.json
   id=<IDs>, date_from=2026-04-01, date_to=2026-04-30,
   metrics=base,events
3. Агрегируй по датам → график
4. Сохрани в Google Sheets (fill-monthly-report.py)
```

### ТОП-10 объявлений по CR
```
1. cli.py GET /api/v3/statistics/banners/day.json (вся кампания)
2. Считай per-banner: clicks→goal_<id> (CR)
3. Отсортируй по CR desc, отрежь top 10
```

### Brand-lift анализ
```
metrics=uniques,uniques_video,video
→ reach, frequency, VTR, уникальные video views per %
```
