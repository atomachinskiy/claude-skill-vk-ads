# VK Ads — ОРД для агентств

## Контекст
С 1 сентября 2022 года реклама в РФ требует маркировки через ОРД (Оператор Рекламных Данных). Если работаешь от агентства — это обязательный цикл. За нарушение — штраф до 500К на организацию.

**ОРД-данные идут в Роскомнадзор автоматически**, если заполнены в API.

---

## 5 шагов ОРД-цикла

### Шаг 1. Заполнить ord_user (ОРД данные агентства)

```bash
cli.py <agency_slug> GET /api/v2/ord_user.json
# если пусто:
cli.py <agency_slug> POST /api/v2/ord_user.json --body '{
  "name": "ИП Иванов Иван Иванович",
  "phone": "79991234567",
  "inn": "123456789012",
  "foreign_inn": "",
  "site": "https://my-agency.ru"
}'
```

Для юр.лица:
```json
{
  "name": "ООО Агентство",
  "phone": "79991234567",
  "inn": "7707123456",
  "site": "https://..."
}
```

### Шаг 2. Добавить клиента с ОРД-реквизитами

Когда агентство принимает нового клиента в работу:

**Клиент = физ.лицо (ИП)**
```bash
cli.py <agency_slug> POST /api/v2/agency/clients.json --body '{
  "user": {"username": "client_login_in_vk"},
  "access_type": "full",
  "is_vkads": true,
  "physical_details": {
    "name": "ИП Иванов И.И.",
    "phone": "79991234567",
    "inn": "1234567890",
    "contract_number": "2026/042",
    "contract_date": "2026-04-15"
  }
}'
```

**Клиент = юр.лицо**
```bash
cli.py <agency_slug> POST /api/v2/agency/clients.json --body '{
  "user": {"username": "client_login_in_vk"},
  "access_type": "full",
  "is_vkads": true,
  "juridical_details": {
    "name": "ООО Ромашка",
    "inn": "7707987654",
    "contract_number": "42/2026",
    "contract_date": "2026-04-15",
    "vat": "with_vat"
  }
}'
```

**Если в цепочке есть подрядчики** (например, рекламное агентство + продакшен + dizain-bureau):
```json
"sub_agents": [
  {"sub_agent_id": 501, "contract_number": "CONTRACT_2026_PROD", "contract_date": "2026-04-01"},
  {"sub_agent_id": 502, "contract_number": "CONTRACT_2026_DESIGN", "contract_date": "2026-04-01"}
]
```

Подрядчиков сначала создаёшь через `ord/partner_sub_agents`.

### Шаг 3. Креативы получают ERID автоматически

После прохождения модерации у каждого баннера появляется поле `erid`:

```bash
cli.py <agency_slug> GET /api/v2/banners/<id>.json --param fields=id,name,erid,moderation_status
# → {"id": 1001, "erid": "2VtzqvQTnKr", "moderation_status": "approved"}
```

ERID **автоматически добавляется** в креатив (VK ставит plash в ленте). В посадку передаётся через UTM `erid=<ERID>` или открыто в URL.

### Шаг 4. Ежемесячно забирать акты

```bash
# Список актов за период
cli.py <agency_slug> GET /api/v2/ord/agency_acts.json \
  --param date_from=2026-04-01 --param date_to=2026-04-30 \
  --param limit=100
```

Поля акта: `id`, `date`, `period_start`, `period_end`, `amount`, `status`.

**Статусы акта:**
- `draft` — формируется
- `ready` — готов, можно скачивать
- `sent_to_ord` — отправлен в ОРД
- `confirmed` — подтверждён ОРД
- `error` — ошибка отправки

Один акт:
```bash
cli.py <agency_slug> GET /api/v2/ord/agency_acts/<id>.json
```

### Шаг 5. Агрегированный отчёт для бухгалтерии

```bash
cli.py <agency_slug> GET /api/v2/ord/agency_report.json \
  --param date_from=2026-04-01 --param date_to=2026-04-30
```

Возвращает:
- Общая сумма
- Количество актов
- Разбивка по клиентам
- Разбивка по подрядчикам

Идеально для Excel-выгрузки в бухгалтерию.

---

## Статус агентства (проверка)

```bash
cli.py <agency_slug> GET /api/v2/ord/agency_status.json
```

Возвращает:
- `registration_status`: `confirmed` / `pending` / `error`
- `confirmed_at`: дата подтверждения

**Если не confirmed** — все креативы пойдут в блокировку ОРД. Без этого шага запускать что-либо бесполезно.

---

## Подрядчики (sub_agents)

### Создать подрядчика
```bash
cli.py <agency_slug> POST /api/v2/ord/partner_sub_agents.json --body '{
  "user_type": "juridical",
  "name": "ООО Продакшен",
  "inn": "7799000123",
  "contract_number": "CONTR_2026_01",
  "contract_date": "2026-01-15",
  "vat": "with_vat"
}'
```
→ `sub_agent_id`, используешь при добавлении клиента

### Обновить
```bash
cli.py <agency_slug> POST /api/v2/ord/partner_sub_agents/<id>.json --body '{
  "contract_number": "CONTR_2026_01_REV2"
}'
```

### Удалить
```bash
cli.py <agency_slug> DELETE /api/v2/ord/partner_sub_agents/<id>.json
```

---

## Для площадок-партнёров (паблишеры)

Если агентство само является площадкой (продаёт размещение у себя на сайте):

### ОРД-данные по площадке
```bash
cli.py <agency_slug> POST /api/v2/ord/partner_pads/<pad_id>.json --body '{
  "name": "example.com",
  "inn": "...",
  "contract_number": "...",
  "contract_date": "..."
}'
```

### Статистика актов по площадке
```bash
cli.py <agency_slug> GET /api/v2/ord/partner_act_stat/<pad_id>.json \
  --param date_from=2026-04-01 --param date_to=2026-04-30
# → impressions, clicks, spend per pad
```

Общая статистика:
```bash
cli.py <agency_slug> GET /api/v2/ord/partner_act_stat.json \
  --param date_from=2026-04-01 --param date_to=2026-04-30
```

---

## Типовые ошибки ОРД

| Ошибка | Причина | Решение |
|---|---|---|
| Креатив в блок без ERID | agency_status != confirmed | Дождаться подтверждения |
| 400 при создании клиента | Нет physical/juridical details | Дозаполнить |
| Акт в status=error | Ошибка отправки в ОРД | Проверить реквизиты клиента |
| ERID не появляется | Креатив на модерации | Ждать approved |
| Нет agency_report | Нет confirmed-актов за период | Проверить что были запуски |

---

## Автоматизация для агентства (ежемесячный пайплайн)

```bash
# 1-го числа каждого месяца:
MONTH_START="2026-05-01"
MONTH_END="2026-05-31"

# Получить статус
cli.py <agency_slug> GET /api/v2/ord/agency_status.json > /tmp/ord_status.json

# Выгрузить акты
cli.py <agency_slug> GET /api/v2/ord/agency_acts.json \
  --param date_from=$MONTH_START --param date_to=$MONTH_END \
  --param limit=500 > /tmp/acts_$MONTH_START.json

# Отчёт
cli.py <agency_slug> GET /api/v2/ord/agency_report.json \
  --param date_from=$MONTH_START --param date_to=$MONTH_END \
  > /tmp/report_$MONTH_START.json

# Отправить в бухгалтерию
# (можно скриптом через Gmail MCP)
```

---

## Чеклист перед запуском рекламы клиента агентства

- [ ] `GET /api/v2/ord/agency_status.json` → confirmed
- [ ] `GET /api/v2/ord_user.json` → заполнен
- [ ] Клиент добавлен через `POST /api/v2/agency/clients.json` с physical_details/juridical_details
- [ ] Все sub_agents заведены если есть цепочка
- [ ] Креативы прошли модерацию → получили ERID
- [ ] В посадке ERID виден (UTM или в URL)

Если любой пункт не выполнен — **не запускай**, иначе трафик в бан.
