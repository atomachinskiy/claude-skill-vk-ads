# VK Ads — Креативы (контент баннеров)

## Типы контента

| Endpoint | Формат | Использование |
|---|---|---|
| `POST /api/v2/content/static.json` | JPG, PNG | Статичные картинки |
| `POST /api/v2/content/video.json` | MP4 | Видео-креативы |
| `POST /api/v2/content/html5.json` | HTML5 (.zip) | Интерактивные баннеры |

Загрузка через multipart:
```bash
cli.py <slug> upload-content ./creative.jpg --kind static
```
→ возвращает `{"id": 777888, ...}` — этот ID идёт в `banner.content.<format>.id`.

---

## Форматы и размеры

### Лента ВК (package 3122)

| Формат | Размер | Соотношение |
|---|---|---|
| Квадратное изображение | 1080×1080 | 1:1 |
| Горизонтальное (baseline) | 1080×607 | 16:9 |
| Портрет | 1080×1350 | 4:5 |
| Карусель — каждая карточка | 1080×1080 | 1:1 |

**Текст (headline + description):**
- Заголовок: до 33 символов (рекомендуется до 25)
- Описание: до 90 символов
- Кнопка CTA: из списка VK

### Stories / Clips (package 3194)

| Формат | Размер | Длина видео |
|---|---|---|
| Vertical video | 1080×1920 | 5-60 сек |
| Vertical image | 1080×1920 | статика |

**Рекомендации:**
- Hook в первые 3 секунды
- Субтитры всегда (большинство смотрит без звука)
- Клик-зоны подальше от краёв (safe area)

### In-stream видео

| Размер | Длительность |
|---|---|
| 1920×1080 (16:9) | 15 / 30 / 60 сек |

### Мобильные (package 3127)

Зависит от sub-формата. Основное:
- 1080×1080 или 1080×1920
- Playable: HTML5-зип до 5МБ

---

## Текстовые блоки

Структура `textblock` в `banner.content`:

```json
{
  "textblocks": [
    {
      "header": "Заголовок (до 33)",
      "title": "Заголовок карточки",
      "description": "Описание (до 90)"
    }
  ]
}
```

Для карусели — массив textblocks, по одному на слайд.

---

## URLs и UTM-разметка

### Создать URL с UTM
```bash
cli.py <slug> POST /api/v2/urls.json --body '{
  "url": "https://example.com/landing?utm_source=vk&utm_medium=cpc&utm_campaign=spring_2026&utm_content=carousel_1"
}'
```
→ возвращает `url_id`

### Получить существующие
```bash
cli.py <slug> GET /api/v2/urls.json --param limit=100
```

### Использование в баннере
```json
"banner": {
  "urls": [{"id": 333444}]
}
```

Или inline (автоматически создаст URL):
```json
"banner": {
  "urls": [{"url": "https://example.com/..."}]
}
```

---

## Audit пиксели (сторонние системы аналитики)

Для подключения сторонних DSP/аналитики (Weborama, Sizmek, DCM):

```bash
# Проверить пиксель
cli.py <slug> POST /api/v2/audit_pixel/check.json --body '{
  "url": "https://pixel.example.com/track?...",
  "pixel_type": "image"
}'

# Сгенерировать
cli.py <slug> GET /api/v2/audit_pixel/generate.json?type=impression&adv_id=...
```

Типы: `impression` (показ), `click`, `post_click`.

Добавление к баннеру:
```json
"banner": {
  "audit_pixels": [
    {"id": ..., "pixel_type": "image", "url": "..."}
  ]
}
```

---

## Коды ошибок загрузки

| Код | Причина | Решение |
|---|---|---|
| `bad_width` | Ширина вне допустимого | Ресайз к точным размерам пакета |
| `bad_height` | Высота вне допустимого | Ресайз |
| `bad_size` | Файл слишком большой | Сжать (JPG ≤2МБ, video ≤200МБ) |
| `bad_type` | Неверный формат файла | Конвертировать в JPG/PNG/MP4 |
| `bad_length` | Видео слишком длинное/короткое | Обрезать в рамки |
| `bad_bitrate` | Битрейт видео вне нормы | Пережать: CRF 23, bitrate 4-8 Mbps |
| `bad_aspect_ratio` | Не то соотношение | Ресайз с точным aspect |

---

## Модерация баннеров

### Статусы
| Status | Значит |
|---|---|
| `new` | Создан, не на модерации |
| `pending` | На модерации (0-24 часа обычно) |
| `approved` | Одобрен, готов к показам |
| `rejected` | Отклонён, нужно исправить |

### Причины отклонения (ModerationReason)
Типовые:
- `forbidden_topic` — запрещённая тематика
- `no_license` — не хватает лицензии (для мед/фин)
- `legal_consent` — нет согласия (152-ФЗ в лид-формах)
- `misleading` — вводит в заблуждение
- `poor_quality` — низкое качество креатива
- `adult_content` — 18+ контент без маркировки
- `comparative_advertising` — сравнительная реклама

### Пере-отправка на модерацию
```bash
cli.py <slug> POST /api/v2/banners/<id>/request_moderation.json
```

После правки креатива / текста. Делай циклом по списку rejected.

### Массовая пере-модерация
Специального mass_action для re-moderation нет — цикл:
```python
for banner_id in rejected:
    cli.py ... POST /api/v2/banners/<id>/request_moderation.json
    sleep(0.5)  # rate limit
```

---

## Banner Fields и Patterns

Разные пакеты требуют разные поля у баннера. Чтобы узнать какие поля обязательны:

```bash
# Поля баннера для пакета
cli.py <slug> GET /api/v2/banner_fields.json --param package_id=3122

# Шаблоны баннеров (для UI)
cli.py <slug> GET /api/v2/banner_patterns.json --param package_id=3122
```

Используй эти ответы чтобы понять структуру `banner.content.*` для нужного формата.

---

## Замена креатива (без пересоздания баннера)

```bash
cli.py <slug> POST /api/v2/banners/<banner_id>.json --body '{
  "content": {
    "image_1080x607": {"id": <new_content_id>}
  }
}'
```

Баннер **снова пойдёт на модерацию** после замены креатива.

---

## Массовая замена (BannerMassReplace)

Если надо заменить один креатив на другой в 100+ баннерах:

```bash
cli.py <slug> POST /api/v2/banners/mass_replace.json --body '{
  "replacements": [
    {"old_banner_id": 1001, "new_banner_id": 2001},
    {"old_banner_id": 1002, "new_banner_id": 2002}
  ]
}'
```

До 200 замен за раз.

---

## Анти-паттерны

❌ **Загрузка без проверки форматов** — API даёт коды ошибок, читай их перед повторной попыткой
❌ **Текст поверх критических зон** — Stories: не ставь текст в нижние 15% (перекрывается UI)
❌ **Слишком плотный текст** — VK модерация срезает «текстовые» креативы (>20% текста на картинке)
❌ **Без субтитров для видео** — 85% смотрят без звука
❌ **Редактирование approved баннера** → статус сбрасывается в `pending`
❌ **Использование чужих лого/скриншотов** — RKN и жалобы
❌ **Слишком много CTA** — одна чёткая призывная кнопка, остальное — info
