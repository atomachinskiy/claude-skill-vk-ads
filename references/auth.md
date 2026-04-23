# VK Ads API — Авторизация

## Base URL
`https://ads.vk.com`

## OAuth 2.0 — три потока

### 1. Client Credentials Grant (обычный клиент)
Используется когда у тебя свой кабинет или клиент дал прямые OAuth-креды.

```
POST /api/v2/oauth2/token.json
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=<APP_ID>
&client_secret=<APP_SECRET>
```

**Ответ:**
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "..."
}
```

### 2. Agency Client Credentials Grant (агентство от имени клиента)
Используется агентством — получить токен для работы в кабинете клиента.

```
POST /api/v2/oauth2/token.json
Content-Type: application/x-www-form-urlencoded

grant_type=agency_client_credentials
&client_id=<AGENCY_APP_ID>
&client_secret=<AGENCY_APP_SECRET>
&agency_client_name=<CLIENT_USERNAME>
```

### 3. Authorization Code Grant (user-facing приложения)
Для приложений с UI где пользователь логинится сам. В нашем скилле не используем — только если будем делать web-интерфейс.

## Refresh Token

Access-токен живёт **24 часа**. Рефреш:

```
POST /api/v2/oauth2/token.json

grant_type=refresh_token
&refresh_token=<REFRESH>
&client_id=<APP_ID>
&client_secret=<APP_SECRET>
```

В `common.py` это автоматически при получении `401 expired_token`.

## Лимиты токенов
- **5 активных токенов** на пару client-user максимум
- Токен удаляется после **1 месяца бездействия**
- При превышении 5 — старые инвалидируются

## Использование токена
```
GET /api/v2/ad_plans.json HTTP/1.1
Host: ads.vk.com
Authorization: Bearer <ACCESS_TOKEN>
```

## Scopes (разрешения приложения)

Scope задаётся **при регистрации OAuth-приложения** — его нельзя добавить потом, только перевыпустить app.

| Scope | Что даёт |
|---|---|
| `read_ads` | Чтение: объекты, статистика |
| `create_ads` | Запись: создание/редактирование рекламных объектов |
| `read_payments` | История платежей, баланс |
| `read_clients` | Агентство: видеть своих клиентов |
| `create_clients` | Агентство: добавлять/удалять клиентов |
| `create_agency_payments` | Агентство: переводы между клиентом и агентством |
| `read_manager_clients` | Менеджер: видеть клиентов в ведении |
| `edit_manager_clients` | Менеджер: редактировать клиентов в ведении |

## Типы пользователей и доступные scopes

| Тип user | Доступные scopes |
|---|---|
| Рекламодатель | read_ads, create_ads, read_payments |
| Агентство | + read_clients, create_clients, create_agency_payments |
| Менеджер | + read_manager_clients, edit_manager_clients |

## Ошибки авторизации

| Код | Что значит | Что делать |
|---|---|---|
| `invalid_token` | Токен неверный / битый | Перевыпустить токен |
| `expired_token` | Access-токен истёк | Рефрешнуть refresh-токеном |
| `invalid_client` | Неверные client_id/secret | Проверить креды в `.env` |
| `invalid_user` | Пользователь недоступен (agency scenario) | Проверить agency_client_name |
| `revoked_token` | Токен отозван пользователем | Запросить перевыпуск OAuth-app |
| `invalid_grant` | Grant type не разрешён | Проверить scope приложения |

## HTTP-коды от API

| Код | Когда |
|---|---|
| 200 / 201 | Успех |
| 204 | Успех без содержимого (например DELETE) |
| 400 | Валидация: `validation_failed`, `bad_value`, `required` |
| 401 | Проблема с токеном |
| 403 | Недостаточно scope |
| 404 | Объект не найден |
| 405 | Метод не разрешён на этом пути |
| 409 | Конфликт (зависимости, дубль) |
| 413 | Тело запроса слишком большое |
| 429 | Rate limit — см. ниже |
| 500 | Серверная ошибка — ретрай через 5-10 сек |

## Rate Limiting

**Headers в каждом ответе:**
```
X-RateLimit-Limit-Second: 10
X-RateLimit-Remaining-Second: 8
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 850
X-RateLimit-Limit-Day: 10000
X-RateLimit-Remaining-Day: 9200
```

**Endpoint для явного чтения лимитов:**
```
GET /api/v2/throttling.json
```

Возвращает текущие лимиты по токену. Используй для smoke-теста при подключении клиента.

**Стратегия при 429:**
- Первый ретрай через 2 сек
- Второй через 5 сек
- Третий через 15 сек
- Дальше логировать и спрашивать пользователя

## Структура ошибки (все эндпоинты)

```json
{
  "error": {
    "code": "validation_failed",
    "message": "Validation failed",
    "fields": {
      "budget_limit": {
        "code": "bad_value",
        "message": "Value must be positive"
      }
    }
  }
}
```

`fields.<field>.code` даёт гранулярную причину.

## Хранение кредов

```
~/.claude/secrets/vk-ads/
├── andrey.env                   # наш кабинет
└── clients/<slug>.env           # клиенты (chmod 600)
```

Формат `.env`:
```
VK_ADS_CLIENT_ID=1234567
VK_ADS_CLIENT_SECRET=abcdef...
VK_ADS_CLIENT_NAME=Название клиента
VK_ADS_ISSUED_AT=2026-04-21
```

Агентский вариант добавляет:
```
VK_ADS_AGENCY_CLIENT_NAME=<клиент_username>
VK_ADS_GRANT_TYPE=agency_client_credentials
```
