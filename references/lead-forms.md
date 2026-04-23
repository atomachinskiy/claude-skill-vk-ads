# VK Ads — Лид-формы и Опросы

## API версия
Всё через `/api/v1/lead_ads/*`.

---

## Структура LeadForm

```
LeadForm
├─ name, status (active/archived)
├─ contact_fields[]          # встроенные поля (phone, email, first_name, city, birth_date)
├─ pages[]                   # страницы формы
│   └─ blocks[]              # блоки на странице
│       ├─ block_type        # question / image / text / ...
│       └─ block_data        # тело блока
│           └─ question      # если type=question
│               ├─ text, type (choice/text/scale)
│               ├─ is_required
│               └─ answers[] # для choice
├─ agreement                 # согласие 152-ФЗ
│   ├─ usage                 # with_template / custom_link
│   └─ template_document     # реквизиты компании
├─ result_info               # экран после отправки
│   ├─ title, description
│   ├─ site_url, cta_text
│   └─ phone
├─ notifications             # webhook/email уведомления
│   └─ destinations[]
│       ├─ type (email/webhook)
│       └─ value (url/email)
├─ promo_code / bonus        # награды (опц)
├─ discount / award
└─ logo_id                   # картинка в шапке (upload_image endpoint)
```

---

## CRUD

### Создать форму
```bash
cli.py <slug> POST /api/v1/lead_ads/lead_forms.json --body /tmp/form.json
```

### Получить одну
```bash
cli.py <slug> GET /api/v1/lead_ads/lead_forms/<id>.json
```

### Список
```bash
cli.py <slug> GET /api/v1/lead_ads/lead_forms.json \
  --param limit=50 --param q=promotions \
  --param _status=active
```

Фильтры:
- `q` — поиск по названию
- `_ad_plan_ids__in` — формы подключённые к кампаниям
- `_ad_group_ids__in` — к группам

### Редактировать
```bash
cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>.json --body /tmp/patch.json
```

### Архивировать (обратимо)
```bash
cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>/archive.json
cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>/unarchive.json
```

### Копировать
```bash
cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>/copy.json
```
Создаёт копию с новым id (для A/B-тестов).

### Загрузить картинку (для logo)
```bash
cli.py <slug> POST /api/v1/lead_ads/lead_forms/upload_image.json \
  --body-file /tmp/logo.png --content-type image/png
```
→ logo_id для использования в форме

---

## Вопросы (LeadFormQuestion)

### Типы
- `text` — открытый ответ
- `choice` — выбор одного из вариантов
- `multichoice` — несколько вариантов
- `scale` — шкала (NPS, рейтинг)

### Пример choice-вопроса
```json
{
  "block_type": "question",
  "block_data": {
    "type": "question",
    "data": {
      "question": {
        "id": 1,
        "text": "Ваш бюджет на рекламу в месяц?",
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
```

### Пример text-вопроса
```json
{
  "question": {
    "id": 2,
    "text": "Опишите задачу в двух словах",
    "type": "text",
    "is_required": false
  }
}
```

### Scale (для NPS)
```json
{
  "question": {
    "id": 3,
    "text": "Насколько вероятно рекомендовать?",
    "type": "scale",
    "scale": {
      "min_value": 0,
      "max_value": 10,
      "step": 1
    }
  }
}
```

---

## Agreement (согласие 152-ФЗ)

Обязательно в форме. Варианты:

### С шаблоном (VK сгенерирует текст)
```json
"agreement": {
  "usage": "with_template",
  "template_document": {
    "company_title": "ООО Ромашка",
    "registration_address": "г. Москва, ул. Примерная, д. 1"
  }
}
```

### Со своей ссылкой
```json
"agreement": {
  "usage": "custom_link",
  "url": "https://example.com/privacy"
}
```

---

## Notifications (уведомления о лидах)

```json
"notifications": {
  "destinations": [
    {"type": "email", "value": "leads@example.com"},
    {"type": "webhook", "value": "https://crm.example.com/vk-webhook"}
  ]
}
```

### Webhook — формат пушa
VK отправляет POST с лидом:
```json
{
  "form_id": 1001,
  "lead_id": 99999,
  "created_at": "2026-04-21T12:34:56Z",
  "contact_info": {
    "phone": "79991234567",
    "first_name": "Иван",
    "email": "ivan@example.com"
  },
  "answers": [
    {"question_id": 1, "answer_options": [2]},
    {"question_id": 2, "text": "Запустить таргетинг"}
  ]
}
```

Webhook endpoint должен отвечать **200 OK** в течение 5 сек.

---

## Награды (promo_code / discount / bonus / award)

После отправки формы клиент получает награду на thank-you экране.

### Промокод
```json
"promo_code": {
  "code": "WELCOME500",
  "discount_percent": 15,
  "discount_amount": 500
}
```

### Бонус
```json
"bonus": {
  "bonus_type": "gift",
  "value": 1000,
  "description": "1000 бонусов на первую покупку"
}
```

### Скидка / Награда
Аналогично, см. объекты `LeadFormDiscount`, `LeadFormAward`.

---

## Лиды — получение и экспорт

### Получить лиды (с пагинацией)
```bash
cli.py <slug> GET /api/v1/lead_ads/lead_forms/<id>/leads.json \
  --param limit=100 --param offset=0
```

Поля ответа: `id`, `form_id`, `ad_plan_id`, `ad_group_id`, `banner_id`, `created_at`, `contact_info`, `answers`.

### Экспорт в CSV / JSON
```bash
cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>/leads/export.json --body '{
  "export_format": "csv"
}'
```

Возвращает URL на скачивание. Файл доступен ~24 часа.

### Тестовый лид (без реальной траты)
```bash
cli.py <slug> POST /api/v1/lead_ads/lead_forms/<id>/test_lead.json --body '{
  "contact_info": {"phone": "79991234567", "first_name": "Test"},
  "answers": [{"question_id": 1, "answer_options": [2]}]
}'
```

Используй ВСЕГДА перед запуском платного трафика — проверь что webhook доходит в CRM.

---

## Привязка формы к ad_group

```bash
cli.py <slug> POST /api/v2/ad_groups/<id>.json --body '{
  "lead_form_id": 1001
}'
```

Одна ad_group = одна лид-форма. Для A/B-теста двух форм — дублируй ad_group с разными `lead_form_id`.

---

## ОПРОСЫ (Survey Forms) — аналогично, но с условной логикой

API: `/api/v1/lead_ads/survey_forms.json`

### Отличия от LeadForm
1. **Условия показа вопросов** (`SurveyCondition`)
2. **Два варианта финала** (positive / negative) для квалификации
3. **Респонденты вместо лидов** (в БД логически отдельно)

### SurveyCondition для перехода
```json
{
  "question": {
    "id": 3,
    "text": "Какой у вас бюджет?",
    "type": "choice",
    "condition": {
      "type": "answer_exists",
      "question_id": 1,
      "answer_id": 2
    }
  }
}
```

«Этот вопрос показывай только если в Q1 был выбран ответ 2».

### Логические операторы условий
```json
"condition": {
  "type": "or",
  "conditions": [
    {"type": "answer_exists", "question_id": 1, "answer_id": 2},
    {"type": "answer_exists", "question_id": 1, "answer_id": 3}
  ]
}
```

Типы: `answer_exists`, `or`, `and`.

### Positive / Negative result

После опроса, на основе ответов, респондент попадает в один из двух экранов:

```json
"result_info": {
  "positive": {
    "title": "Вы нам подходите!",
    "description": "Мы свяжемся в течение 30 минут",
    "cta_text": "Ожидаю звонка",
    "site_url": "https://example.com/thanks"
  },
  "negative": {
    "title": "К сожалению, мы пока не можем помочь",
    "description": "Но спасибо за интерес!",
    "cta_text": "На главную",
    "site_url": "https://example.com/"
  }
}
```

Логика positive/negative программируется через conditions (VK-side не проверяет — ты задаёшь "какой ответ = positive").

---

## Экспорт ответов опроса

```bash
cli.py <slug> POST /api/v1/lead_ads/survey_forms/<id>/respondents/export.json \
  --body '{"export_format": "csv"}'
```

---

## Типовые кейсы

### Короткая форма на лид (b2c, массовая ниша)
```
contact_fields: phone, first_name
1 страница, 0-1 квал-вопросов
agreement: with_template
notifications: email + webhook
promo_code: "WELCOME15"
```

### Квал b2b
```
contact_fields: phone, first_name, email, company
2 страницы:
  - стр1: бюджет, срочность, ниша
  - стр2: контакты + комментарий
Survey c SurveyCondition (бюджет <50К → negative)
notifications: webhook (в CRM с меткой "квал")
```

### Кастдев / NPS
```
Survey с scale-вопросами
10 вопросов на разные аспекты продукта
result_info positive: "Спасибо за feedback"
```

---

## Анти-паттерны

❌ **Без test_lead перед запуском** — узнаешь о проблеме с webhook только после спуска бюджета
❌ **Webhook endpoint отвечает >5 сек** — VK зафейлит и не ретраит (потеряешь лид)
❌ **Слишком много вопросов (>5)** — CR падает экспоненциально, не более 3-4 на массовом трафике
❌ **Нет agreement** → форма не пройдёт модерацию
❌ **Неверные контакт-поля** — у физ.лиц не просим компанию, у b2b просим
