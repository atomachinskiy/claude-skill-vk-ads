# VK Ads — Массовые операции

## Главное правило: **200 объектов за один запрос**

Если объектов больше — дели на батчи. API вернёт 400 при превышении.

---

## Доступные массовые операции

### 1. Смена статуса баннеров
```bash
cli.py <slug> POST /api/v2/banners/mass_action.json --body '{
  "id": [1001, 1002, 1003],
  "status": "blocked"
}'
```
Статусы: `active` | `blocked` | `deleted`.

### 2. Смена статуса групп
```bash
cli.py <slug> POST /api/v2/ad_groups/mass_action.json --body '{
  "id": [501, 502, 503],
  "status": "active"
}'
```

### 3. Смена статуса кампаний
```bash
cli.py <slug> POST /api/v2/ad_plans/mass_action.json --body '{
  "id": [101, 102],
  "status": "blocked"
}'
```

### 4. Массовая замена креативов
```bash
cli.py <slug> POST /api/v2/banners/mass_replace.json --body '{
  "replacements": [
    {"old_banner_id": 1001, "new_banner_id": 2001},
    {"old_banner_id": 1002, "new_banner_id": 2002}
  ]
}'
```

### 5. Массовое обновление таргетингов
```bash
cli.py <slug> POST /api/v2/ad_groups/targetings_mass_action.json --body '{
  "id": [501, 502, 503],
  "targetings": {
    "geo": {"regions": [5506, 5525]},
    "age_targeting": {"age_from": 25, "age_to": 50}
  }
}'
```
Перезаписывает таргетинги полностью.

### 6. Массовое обновление возраста
```bash
cli.py <slug> POST /api/v2/ad_groups/age_targeting_mass_action.json --body '{
  "id": [501, 502, 503],
  "age_targeting": {"age_from": 30, "age_to": 55}
}'
```
Точечное обновление только возраста, остальные таргетинги не трогаются.

### 7. Пакетное обновление товаров каталога (NDJSON)
```bash
cli.py <slug> POST /api/v2/remarketing/pricelists/<id>/batch.json \
  --body-file products.ndjson \
  --content-type application/x-ndjson
```

Формат (одна строка = одна операция):
```
{"method":"PUT","data":{"id":"sku001","title":"...","price":49900,...}}
{"method":"PUT","data":{"id":"sku002",...}}
{"method":"DELETE","data":{"id":"sku999"}}
```

**Лимит:** до 200 МБ за батч. Если каталог больше — режь.

Возвращает `task_id`, проверка статуса:
```bash
cli.py <slug> GET /api/v2/remarketing/pricelists/<id>/batch/<task_id>.json
# status: pending / process / done / error
```

---

## Батчинг больше 200 объектов

```python
# псевдокод
all_ids = [1001, 1002, ..., 1750]  # 750 объектов

for batch in chunks(all_ids, 200):  # 200, 200, 200, 150
    cli.py POST /api/v2/ad_groups/mass_action.json --body {
        "id": batch, "status": "blocked"
    }
    sleep(0.5)  # rate limit
```

В скриптах скилла этот паттерн уже зашит в `manage.py` и `create.py` где нужно.

---

## Что НЕТ в массовых (но часто хочется)

| Хочется | Альтернатива |
|---|---|
| Массовое изменение бюджетов | Цикл по `POST /ad_groups/<id>.json` с rate limit |
| Массовая пере-модерация | Цикл по `POST /banners/<id>/request_moderation.json` |
| Массовое обновление priced_goal | Цикл по `POST /ad_groups/<id>.json` |
| Массовое создание баннеров | Цикл по `POST /banners.json` (нельзя одним запросом) |
| Массовое создание сегментов | Цикл |

Для циклов используй `sleep(0.3-0.5)` между вызовами + обработку 429 с экспоненциальным бэкофом.

---

## Типовые кейсы

### Пауза всех кампаний клиента на выходные
```python
# Получить активные
ids = get_all_active_ad_plan_ids(slug)

# Пауза массово
for batch in chunks(ids, 200):
    cli.py <slug> POST /api/v2/ad_plans/mass_action.json --body {
        "id": batch, "status": "blocked"
    }

# В понедельник обратно
for batch in chunks(ids, 200):
    cli.py <slug> POST /api/v2/ad_plans/mass_action.json --body {
        "id": batch, "status": "active"
    }
```

### Смена креатива в 300 баннерах (сезонная акция)
```python
# 1. Загрузить новый креатив
new_content_id = upload(new_creative)
# 2. Создать "шаблонный" баннер с новым креативом (если нужен именно новый банер)
new_banner = create_banner(content_id=new_content_id, urls=...)
# 3. Получить старые баннеры (300 шт)
old_ids = get_active_banners(...)
# 4. Массовая замена (батчами по 200)
for batch_pairs in chunks(pairs, 200):
    cli.py POST /api/v2/banners/mass_replace.json --body {
        "replacements": [{"old_banner_id": o, "new_banner_id": n} for o, n in batch_pairs]
    }
```

### Широкая смена гео (добавили города)
```python
# Обновить таргетинги у всех групп кампании
ids = get_ad_groups_in_campaign(campaign_id)
for batch in chunks(ids, 200):
    cli.py POST /api/v2/ad_groups/targetings_mass_action.json --body {
        "id": batch,
        "targetings": {
            "geo": {"regions": [5506, 5525, 5499, 5503]}
        }
    }
```

**ВНИМАНИЕ:** targetings_mass_action **перезаписывает** все таргетинги. Если нужно только ДОБАВИТЬ гео — сначала получить текущие таргетинги и отправить объединённые.

### Архивация кампаний старше 6 месяцев
```python
# Получить старые
old = cli.py GET /api/v2/ad_plans.json --param date_end__lte=<полгода назад>
ids = [x.id for x in old]

# Удалить (через status=deleted, не hard-delete)
for batch in chunks(ids, 200):
    cli.py POST /api/v2/ad_plans/mass_action.json --body {
        "id": batch, "status": "deleted"
    }
```

---

## Ошибки массовых операций

| Ошибка | Причина | Решение |
|---|---|---|
| 400 `batch_too_large` | >200 объектов | Режь на батчи |
| 400 `invalid_ids` | Несуществующие ID в списке | Фильтровать до отправки |
| 400 `invalid_status` | Неверный статус | Только `active/blocked/deleted` |
| 429 Too Many | Rate limit | sleep + retry |
| 200 с ошибками per-item | Часть провалилась | Читай response.errors[] |

Ответ mass_action содержит:
```json
{
  "successful": [1001, 1002],
  "failed": [
    {"id": 1003, "error": {"code": "not_found"}}
  ]
}
```

Логируй `failed[]` и разбирайся отдельно.

---

## Подтверждение перед массовкой (критично!)

**Любая массовая операция на чужом кабинете — через подтверждение Андрея.**

Пример запроса подтверждения в TG перед массовой паузой:
```
Готов отправить: pause 47 кампаний клиента <X>
Campaign IDs: 1001, 1002, ...
Причина: конец месяца, бюджет исчерпан
Подтверди — пущу.
```

Случайная пауза 100+ кампаний → потеря выручки за сутки.

---

## Связанные endpoints (не mass_action но полезны)

### Удалить множественные relations из сегмента
```bash
cli.py <slug> DELETE /api/v2/remarketing/segments/<id>/relations.json \
  --param relation_id__in=1001,1002,1003
```
До ~100 relations за запрос.

### Получить множество объектов сразу (bulk GET)
```bash
cli.py <slug> GET /api/v2/banners.json \
  --param _id__in=1001,1002,1003 --param limit=200
```
Обходит `GET /banners/<id>.json` в цикле — 1 запрос вместо 200.
