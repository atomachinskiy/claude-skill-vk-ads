# VK Ads — Рабочие рецепты

Готовые сценарии для типовых задач. Копируй, подставляй ID.

---

## Рецепт 1: Запуск новой кампании на холодную ЦА

```
Шаг 1. Прогноз охвата (projection)
─────────────────────────────────
Цель: валидировать что бюджет и таргет реалистичны до старта.

1.1. Создай временный "черновик" ad_plan с нужными ad_groups+targetings
1.2. POST /api/v2/ad_plans/<ad_plan_id>/projection.json
1.3. Смотри impressions_min/max, clicks_min/max, CPM/CPC
1.4. Если прогноз < 50% от задачи — расширяй таргет или бюджет

Шаг 2. Загрузка креативов
─────────────────────────
cli.py <slug> upload-content ./creative.jpg --kind static
→ получил content_id (например 777888)

Шаг 3. Создание URL с UTM
─────────────────────────
cli.py <slug> POST /api/v2/urls.json --body '{
  "url": "https://example.com/landing?utm_source=vk&utm_medium=cpc&utm_campaign=spring_2026"
}'
→ url_id (например 333444)

Шаг 4. Создание кампании
────────────────────────
create.py <slug> campaign --body /tmp/plan.json --dry-run
create.py <slug> campaign --body /tmp/plan.json
→ ad_plan_id

Шаг 5. Проверь модерацию через 1-2 часа
───────────────────────────────────────
cli.py <slug> GET /api/v2/banners.json --param _ad_plan_id=<id> \
  --param fields=id,name,moderation_status
→ pending / approved / rejected

Шаг 6. Запусти через 3-7 дней learning phase
────────────────────────────────────────────
НЕ меняй настройки в это время.
```

---

## Рецепт 2: Параллельный ретаргет счётчик сайта

Когда запускаешь холодную кампанию — **всегда** параллельно ставь ретаргет на счётчик.

```
1. Убедись что счётчик Top@Mail.ru стоит на сайте
   cli.py <slug> GET /api/v2/remarketing/counters.json
   → system_status: active, working: true

2. Создай сегмент "Все посетители сайта за 180 дней"
   cli.py <slug> POST /api/v2/remarketing/segments.json --body '{
     "name": "Site_visitors_180d",
     "pass_condition": 1,
     "relations": [
       {"object_type":"remarketing_counter","object_id":<counter_id>,
        "params":{"type":"positive","left":0,"right":180}}
     ]
   }'
   → segment_id

3. Создай ещё одну ad_group в уже работающей кампании
   targetings = таргет холодной + segments = [segment_id]
   (гео/возраст/пол шире чем холодная — пусть захватывает хвост)

4. Бюджет ретаргета = 15-25% от холодного бюджета
5. Priced_goal ниже чем у холодного (дешевле конверсия)
```

**Результат:** 5-15% дополнительных конверсий при CPA в 2-5 раз ниже холодного.

---

## Рецепт 3: Загрузка базы из CRM и запуск LAL

```
1. Выгрузи телефоны/email из CRM в TXT (по одному на строку)
   → /tmp/crm_buyers.txt

2. Загрузи как аудиторию
   upload-audience.py <slug> "CRM_buyers_2026" /tmp/crm_buyers.txt --kind phone
   → users_list_id (скрипт покажет)

3. Проверь match-rate через 5-10 минут
   cli.py <slug> GET /api/v2/remarketing/users_lists/<id>.json
   → users_count: сколько реально смэтчилось
   (Норма 40-70% от исходного файла)

4. Создай LAL через UI кабинета (API для LAL ограничен)
   → lal_segment_id

5. Создай ad_group с targetings.segments = [lal_segment_id]
   Бюджет начни с 20-30К на тест, priced_goal чуть выше холодной
```

---

## Рецепт 4: Массовая пауза всех кампаний клиента (конец месяца)

```
1. Получи все активные кампании клиента
   cli.py <slug> GET /api/v2/ad_plans.json \
     --param _status=active --param limit=200 \
     --param fields=id,name
   → список IDs

2. Если >200 — дели на батчи

3. Массовая пауза
   cli.py <slug> POST /api/v2/ad_plans/mass_action.json --body '{
     "id": [1001,1002,...,1200],
     "status": "blocked"
   }'

4. Подтверди у Андрея перед выполнением (чужой бюджет!)
```

---

## Рецепт 5: Отчёт для клиента за месяц в Google Sheets

```
1. Используй готовый скрипт
   fill-monthly-report.py <slug> 2026-04

Если <slug>.json нет в clients/:
2. Собери маппинг кампаний → названия продуктов
   cli.py <slug> GET /api/v2/ad_plans.json --param _status=active,blocked \
     --param fields=id,name → JSON
3. Вручную сверь с клиентом какая кампания = какой продукт
4. Сохрани в clients/<slug>.json (см. templates/client-template.json)

Что заполняет скрипт:
- Строки: по каждой кампании / дню
- Колонки: Потрачено, Показы, Клики, CTR, CPC, CPM, Конверсии, CPA
- Формулы CTR/CPC остаются в шаблоне клиента (НЕ перезаписывать)
```

---

## Рецепт 6: Лид-форма с квалификацией

```
1. Создай форму
   cli.py <slug> POST /api/v1/lead_ads/lead_forms.json --body '{
     "name": "Квал b2b услуги",
     "contact_fields": ["phone", "first_name", "email"],
     "pages": [
       {
         "blocks": [
           {
             "block_type": "question",
             "block_data": {
               "type": "question",
               "data": {
                 "question": {
                   "text": "Ваш ежемесячный бюджет на рекламу?",
                   "type": "choice",
                   "is_required": true,
                   "answers": [
                     {"id": 1, "text": "До 50К"},
                     {"id": 2, "text": "50-200К"},
                     {"id": 3, "text": "200-500К"},
                     {"id": 4, "text": "500К+"}
                   ]
                 }
               }
             }
           }
         ]
       }
     ],
     "result_info": {
       "title": "Спасибо!",
       "description": "Мы свяжемся в течение 30 минут",
       "cta_text": "На главную",
       "site_url": "https://example.com"
     },
     "agreement": {
       "usage": "with_template",
       "template_document": {
         "company_title": "ООО Ромашка",
         "registration_address": "Москва, ..."
       }
     },
     "notifications": {
       "destinations": [
         {"type": "email", "value": "leads@example.com"},
         {"type": "webhook", "value": "https://crm.example.com/vk-webhook"}
       ]
     }
   }'
   → lead_form_id

2. Отправь тестовый лид
   cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>/test_lead.json --body '{
     "contact_info": {"phone": "79991234567", "first_name": "Тест"},
     "answers": [{"question_id": 1, "answer_options": [2]}]
   }'
   → проверь что webhook пришёл в CRM, email доставлен

3. Привяжи к ad_group
   cli.py <slug> POST /api/v2/ad_groups/<id>.json --body '{
     "lead_form_id": <lead_form_id>
   }'

4. Через неделю — экспорт лидов
   cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>/leads/export.json \
     --body '{"export_format": "csv"}'
```

---

## Рецепт 7: ОРД-цикл для нового клиента агентства

```
ШАГ 1. Проверь статус агентства
cli.py <agency_slug> GET /api/v2/ord/agency_status.json
→ если не confirmed, без этого ни одна кампания не пойдёт

ШАГ 2. Убедись что у агентства заполнен ord_user
cli.py <agency_slug> GET /api/v2/ord_user.json
→ если пусто — заполни через POST (name, inn, contract_number)

ШАГ 3. Добавь клиента с ОРД-деталями
cli.py <agency_slug> POST /api/v2/agency/clients.json --body '{
  "user": {"username": "client_login"},
  "physical_details": {          # или juridical_details
    "name": "ИП Иванов И.И.",
    "phone": "79991234567",
    "inn": "1234567890",
    "contract_number": "2026/042",
    "contract_date": "2026-04-15"
  },
  "sub_agents": [                # если в цепочке есть подрядчики
    {"sub_agent_id": 999}
  ],
  "access_type": "full"
}'

ШАГ 4. Креативы получают ERID автоматически после модерации
Проверяй ERID в ответе GET /api/v2/banners/<id>.json → erid

ШАГ 5. Конец месяца — забирай акты
cli.py <agency_slug> GET /api/v2/ord/agency_acts.json \
  --param date_from=2026-04-01 --param date_to=2026-04-30

cli.py <agency_slug> GET /api/v2/ord/agency_report.json \
  --param date_from=2026-04-01 --param date_to=2026-04-30
→ агрегированный отчёт для бухгалтерии
```

---

## Рецепт 8: Прогноз охвата перед крупным запуском

```
1. Сформируй projection-body с теми таргетами что планируешь
   {
     "ad_groups": [
       {
         "package_id": 3122,
         "budget_limit": 100000,
         "targetings": {
           "geo": {"regions": [5506]},
           "age_targeting": {"age_from": 25, "age_to": 55},
           "sex": [1]
         }
       }
     ]
   }

2. POST /api/v2/ad_plans/<existing_ad_plan_id>/projection.json
   (нужен существующий ad_plan_id — можно из любой черновой кампании)

3. Ответ содержит:
   - predicted_rates: ставки
   - projection: impressions_min/max, clicks_min/max, reach_min/max
   - targetings: по каждому таргетингу охват

4. Рассчитай ожидаемый CPM = budget / impressions * 1000
   Сравни с рыночным. Если >> рынка — таргет узкий, расширяй.

5. Покажи клиенту цифры ПЕРЕД стартом.
```

---

## Рецепт 9: Динамический ретаргет (товарный каталог)

```
1. Создай pricelist (через UI или API)
   → pricelist_id

2. Сформируй NDJSON с товарами
   products.ndjson:
   {"method":"PUT","data":{"id":"sku001","title":"...","price":49900,...}}
   {"method":"PUT","data":{"id":"sku002",...}}

3. Загрузи батч
   cli.py <slug> POST /api/v2/remarketing/pricelists/<id>/batch.json \
     --body-file products.ndjson --content-type application/x-ndjson
   → task_id

4. Подожди 1-5 минут, проверь статус
   cli.py <slug> GET /api/v2/remarketing/pricelists/<id>/batch/<task_id>.json
   → done / error

5. Создай ad_group с pricelist_id + тип dynamic_retargeting
   Движок сам будет показывать товары которые смотрел пользователь.

6. Статистика в metric-set ad_offers (product-level)
```

---

## Рецепт 10: Повторная отправка отклонённых баннеров на модерацию

```
1. Найди все rejected баннеры
   cli.py <slug> GET /api/v2/banners.json \
     --param _moderation_status=rejected \
     --param fields=id,name,moderation_reasons \
     --param limit=200
   → список IDs + причины

2. Прочитай причины (не все reject'ы исправимы)
3. Исправь креатив / текст / URL
4. Замени креатив (если проблема в картинке)
   cli.py <slug> POST /api/v2/banners/<id>.json --body '{
     "content": {...new content_id...}
   }'

5. Отправь на ре-модерацию
   for banner_id in rejected_ids:
     cli.py <slug> POST /api/v2/banners/<id>/request_moderation.json
   
   (нет mass_action специально для remod, делаем циклом)
```

---

## Рецепт 11: Фильтрация стату по окну конверсии

Клиент: «покажи какие группы конвертят дешевле 500₽ на лид».

```
1. Выгрузи стату v3 за период
   cli.py <slug> GET /api/v3/statistics/ad_groups/day.json \
     --param date_from=2026-04-01 --param date_to=2026-04-30 \
     --param metrics=base,events --param limit=250

2. Агрегируй per ad_group:
   - spent = sum(spent по дням)
   - conversions = sum(goal_<id>)
   - CPA = spent / conversions

3. Отфильтруй: CPA < 500

4. Сортируй по conversions desc — это топ-группы
```

---

## Рецепт 12: Копирование успешной кампании на новый месяц

```
1. Получи кампанию с полной структурой
   cli.py <slug> GET /api/v2/ad_plans/<id>.json --param fields=all
   → полный JSON

2. Очисти id-шники (id, created, updated, status=deleted на внутренних)
3. Измени name, date_start, date_end на новый месяц
4. Создай новую
   cli.py <slug> POST /api/v2/ad_plans.json --body /tmp/plan_copy.json

5. Статистика перенесённой кампании остаётся в старой (ID разные)
   Агрегация в отчёте клиента: суммируй обе через fill-monthly-report
```
