# VK Ads — Аудитории и Сегменты

## Иерархия объектов

```
RemarketingCounter (счётчик Top@Mail.ru — источник данных с сайта)
  └─ CounterGoals (цели: покупка, корзина, регистрация, просмотр)

RemarketingUsersList (загруженный список телефонов / email, SHA256)

LocalGeo (точки на карте с радиусами)

RemarketingOfflineGoals (оффлайн-конверсии — POS, CRM)

RemarketingInAppEvents (мобильные события — installs, opens, purchases)

RemarketingPricelist (товарный каталог)

   ↓ всё выше → входит в...

Segment (комбинация с логикой pass_condition)
  ├─ relations (массив источников)
  └─ pass_condition (минимум соответствий, 1..len(relations))

SharingKey (расшаривание сегмента другим кабинетам)
```

---

## 1. Счётчики Top@Mail.ru

### Подключить счётчик
```bash
cli.py <slug> POST /api/v2/remarketing/counters.json --body '{
  "counter_id": 1234567,
  "domain": "example.com"
}'
```

### Получить список
```bash
cli.py <slug> GET /api/v2/remarketing/counters.json
```

### Статусы счётчика
- `working` — boolean, работает ли
- `system_status` — active/pending/error
- Если error — проверить установку кода на сайте

### Цели в счётчике
```bash
# Список
cli.py <slug> GET /api/v2/remarketing/counters/<counter_id>/goals.json

# Создать
cli.py <slug> POST /api/v2/remarketing/counters/<counter_id>/goals.json --body '{
  "name": "Покупка",
  "type": "url",
  "conditions": {"url": "/thanks"}
}'
```

Типы целей:
- `url` — попадание на URL
- `event` — кастомное событие из JS-кода
- `duration` — время на сайте ≥ N секунд
- `pages` — просмотр ≥ N страниц
- `form` — отправка формы

Получить ВСЕ цели (всех счётчиков): `GET /api/v2/remarketing/goals.json`.

---

## 2. Списки пользователей (loaded contacts)

### Загрузка через upload-audience.py
```bash
# Из файла телефонов
scripts/upload-audience.py <slug> "База покупателей 2026" \
  ~/audiences/buyers.txt --kind phone

# Email
scripts/upload-audience.py <slug> "Email база" emails.txt --kind email

# Mixed
scripts/upload-audience.py <slug> "Контакты" contacts.txt --kind mixed

# Уже SHA256
scripts/upload-audience.py <slug> "Хешированные" hashes.txt --already-hashed
```

### Под капотом скрипт делает

1. Нормализация телефона:
   - `+7 (123) 456-78-90` → `71234567890`
   - `8 123 456 78 90` → `71234567890`
   - `9991234567` → `79991234567`
2. Email → lowercase + trim
3. SHA256 каждого значения → hex
4. `POST /api/v2/remarketing/users_lists.json`:
   ```json
   {
     "name": "...",
     "type": 1,
     "users": "<hash1>,<hash2>,..."
   }
   ```

### Типы списков
- `type=1` — фиксированный список (загружен раз)
- `type=2` — растущий (дополняется через append)

### Лимиты
- Рекомендуемый **минимум 1000 контактов** для нормального матчинга
- Типичный match-rate по РФ: 40-70% (зависит от актуальности базы)
- Файл до ~10МБ за загрузку (режь большие файлы на батчи)

### 152-ФЗ (важно!)
Контакты можно грузить только при наличии **согласия** клиента на обработку ПД для целей рекламы. «Серые» базы грузить нельзя — штраф и блок кабинета.

---

## 3. Оффлайн-конверсии

Для клиентов с розницей / CRM-покупками:

```bash
# Создать оффлайн-цель
cli.py <slug> POST /api/v2/remarketing/offline_goals.json --body '{
  "name": "Покупка в рознице"
}'

# Загрузить события (user_id из Mail.ru или хэш-контакты)
cli.py <slug> POST /api/v2/remarketing/offline_goals/<id>/events.json --body '{
  "users": [
    {"phone_sha256": "...", "timestamp": 1713705600, "value": 12500}
  ]
}'
```

Используется для:
- Атрибуции офлайн-покупок к онлайн-кампаниям
- Сегмента «купили онлайн + оффлайн»
- ROMI с учётом оффлайн-выручки

---

## 4. InApp события (мобильные)

Для мобильных приложений связка:

1. Подключить app: `/api/v2/apple_apps/<app_name>.json` (iOS) или `/api/v2/google_apps/<app_name>.json`
2. Категории событий: `/api/v1/inapp_event_categories.json`
3. Создать событие: `/api/v2/inapp_events/<id>.json`
4. Настроить трекер (AppsFlyer / Adjust / AppMetrica)

Используется в таргетингах как `remarketing_inapp_events`.

---

## 5. LocalGeo (геозоны)

Переиспользуемые геозоны:

```bash
# Создать
cli.py <slug> POST /api/v2/local_geos.json --body '{
  "name": "Салоны Москва центр",
  "geo_points": [
    {"latitude": 55.7558, "longitude": 37.6176, "radius": 2000},
    {"latitude": 55.7622, "longitude": 37.6094, "radius": 1500}
  ]
}'

# Получить список
cli.py <slug> GET /api/v2/local_geos.json
```

В targetings: `"local_geo": {"id": 123}` (ссылаемся по ID вместо inline-описания).

---

## 6. Сегменты — сердце аудитории

### Создать сегмент
```bash
cli.py <slug> POST /api/v2/remarketing/segments.json --body '{
  "name": "Корзина 30 дней БЕЗ покупки",
  "pass_condition": 1,
  "relations": [
    {
      "object_type": "remarketing_counter_goal",
      "object_id": 5001,
      "params": {"type": "positive", "left": 0, "right": 30}
    },
    {
      "object_type": "remarketing_counter_goal",
      "object_id": 5002,
      "params": {"type": "negative", "left": 0, "right": 30}
    }
  ]
}'
```

### pass_condition логика
- `pass_condition=1` — достаточно 1 relation (OR)
- `pass_condition=2` — нужно 2+ relations (AND-подобно)
- Максимум `pass_condition` = количество relations

### Типы relations (`object_type`)
- `remarketing_counter` — все посетители счётчика
- `remarketing_counter_goal` — посетители с целью
- `remarketing_users_list` — загруженный список
- `remarketing_offline_goal` — оффлайн-конверсия
- `remarketing_inapp_event` — мобильное событие

### Params внутри relation
- `type: "positive"` — пользователь **выполнил**
- `type: "negative"` — пользователь **НЕ выполнил**
- `left`, `right` — окно в днях (0..180 обычно)

### Типовые рецепты сегментов

**«Посетили сайт за 7 дней И не купили»**
```json
{
  "pass_condition": 2,
  "relations": [
    {"object_type": "remarketing_counter", "object_id": 1001,
     "params": {"type": "positive", "left": 0, "right": 7}},
    {"object_type": "remarketing_counter_goal", "object_id": 5002,
     "params": {"type": "negative", "left": 0, "right": 30}}
  ]
}
```

**«Корзина И не покупка И не добавил повторно 14 дней»**
```json
{
  "pass_condition": 3,
  "relations": [
    {"object_type": "remarketing_counter_goal", "object_id": 5001 /*корзина*/,
     "params": {"type": "positive", "left": 0, "right": 30}},
    {"object_type": "remarketing_counter_goal", "object_id": 5002 /*покупка*/,
     "params": {"type": "negative", "left": 0, "right": 30}},
    {"object_type": "remarketing_counter_goal", "object_id": 5001,
     "params": {"type": "negative", "left": 0, "right": 14}}
  ]
}
```

**«Купили онлайн + оффлайн за квартал»**
```json
{
  "pass_condition": 1,
  "relations": [
    {"object_type": "remarketing_counter_goal", "object_id": 5002,
     "params": {"type": "positive", "left": 0, "right": 90}},
    {"object_type": "remarketing_offline_goal", "object_id": 701,
     "params": {"type": "positive", "left": 0, "right": 90}}
  ]
}
```

---

## 7. SharingKeys — расшаривание сегмента

Используется агентствами чтобы один сегмент можно было подставлять в разных клиентских кабинетах.

```bash
# Создать ключ к сегменту
cli.py <slug_headquarters> POST /api/v2/sharing_keys.json --body '{
  "segment_id": 10001
}'
# → sharing_key_id и key_value

# Добавить пользователей, которые могут использовать
cli.py <slug_headquarters> POST /api/v2/sharing_keys/<key_id>/users.json --body '{
  "user_id": 999888,
  "access_type": "read"
}'
```

---

## 8. Pricelist (товарные каталоги)

Для динамического ретаргета:

```bash
# Создать прайс-лист (через UI обычно)
# Обновление товаров (NDJSON, batch до 200МБ)
cli.py <slug> POST /api/v2/remarketing/pricelists/<id>/batch.json \
  --body-file /tmp/products.ndjson \
  --content-type application/x-ndjson
```

Формат NDJSON (одна строка = один товар):
```json
{"method":"PUT","data":{"id":"sku001","title":"Диван Модерн","price":49900,"url":"...","image_url":"...","category":"furniture"}}
{"method":"PUT","data":{"id":"sku002","title":"Кресло","price":19900,...}}
{"method":"DELETE","data":{"id":"sku999"}}
```

Проверка статуса:
```bash
cli.py <slug> GET /api/v2/remarketing/pricelists/<id>/batch/<task_id>.json
# status: pending / process / done / error
```

В error-ответе:
- `feed_failure` — критичная ошибка (весь файл не применился)
- `offer_error` — конкретные товары отклонены
- `offer_warning` — прошли с предупреждением

---

## 9. Лимиты и анти-паттерны

- Максимум **10 000 сегментов** на пользователя
- **Циклы запрещены** — сегмент не может ссылаться на себя
- **pass_condition > len(relations)** — валидация завалится
- При удалении сегмента который **используется в ad_group** — 409 conflict, сначала убери из групп
- **Лимиты на списки:** >1000 контактов рекомендуется, <100 почти не работает
- **SharingKey удаляется → сегмент пропадает** у всех пользователей ключа
