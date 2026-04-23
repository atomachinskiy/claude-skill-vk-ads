# VK Ads API Каталог — Полный Реестр Эндпоинтов и Объектов

**Дата каталогизации:** 21 апреля 2026  
**Источник:** Офиц. документация VK Ads API (https://ads.vk.com/help/api)  
**Назначение:** Справочный реестр для AI-таргетолога (профессиональный скилл)

---

## ЧАСТЬ 1: МЕТОДЫ (ЭНДПОИНТЫ)

### 1. ПОЛЬЗОВАТЕЛИ (6 эндпоинтов)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-AgencyClients | `/api/v2/agency/clients.json` | GET, POST | Получить/создать клиентов агентства | limit, offset, _user__id, _user__status, access_type | AgencyClient, User |
| 02-AgencyManagerClient | `/api/v2/agency/managers/<manager_id>/clients/<client_id>.json` | POST, DELETE | Управление клиентом в ведении менеджера | access_type | AgencyManagerClient |
| 03-User | `/api/v3/user.json` | GET, POST | Получить/обновить профиль пользователя | info_currency, language, email_settings, mailings | User |
| 04-ManagerClients | `/api/v3/manager/clients.json` | GET | Получить клиентов менеджера | limit, offset, _user__id, _status | UserManagerClient |
| 05-AgencyClient | `/api/v2/agency/clients/<id>.json` | POST, DELETE | Редактировать/удалить клиента агентства | is_vkads, access_type | AgencyClient |
| 06-OrdUser | `/api/v2/ord_user.json` | GET, POST | Управлять ОРД данными физ. лица | name, phone, inn, foreign_inn | OrdUser |

---

### 2. СПРАВОЧНИКИ (10 эндпоинтов)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-AppleApp | `/api/v2/apple_apps/<app_name>.json` | GET, POST | Получить/обновить информацию о приложении App Store | app_name (ID) | AppleApp |
| 02-GoogleApp | `/api/v2/google_apps/<app_name>.json` | GET, POST | Получить/обновить информацию о приложении Google Play | app_name (package_id) | GoogleApp |
| 03-InAppEventCategories | `/api/v1/inapp_event_categories.json` | GET | Получить категории событий в мобильном приложении | - | InAppEventCategories |
| 04-MobileCategory | `/api/v2/mobile_categories.json` | GET | Получить категории мобильных приложений | - | MobileCategory |
| 05-MobileOperationSystem | `/api/v2/mobile_os.json` | GET | Получить список мобильных ОС | - | MobileOperationSystem |
| 06-MobileOperator | `/api/v2/mobile_operators.json` | GET | Получить операторов мобильных сетей | - | MobileOperator |
| 07-MobileTypes | `/api/v2/mobile_types.json` | GET | Получить типы мобильных устройств | - | MobileTypes |
| 08-MobileVendors | `/api/v2/mobile_vendors.json` | GET | Получить производителей мобильных устройств | - | MobileVendors |
| 09-Region | `/api/v2/regions.json` | GET | Получить географические регионы с фильтрацией | _id, _parent_id, _flags, _q, Accept-Language | Region |
| 10-UserGeo | `/api/v2/user_geo.json` | GET | Получить регионы, указанные пользователями | limit, offset, _id, _q | UserGeo |

---

### 3. РЕКЛАМНЫЕ ОБЪЕКТЫ (27 эндпоинтов)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-BannerMassAction | `/api/v2/banners/mass_action.json` | POST | Массово обновить статусы баннеров (max 200 за раз) | id, status | BannerMassAction |
| 02-Content | `/api/v2/content/(static\|video\|html5).json` | POST | Загрузить креативы (статичные, видео, HTML5) | file, width, height, data | Content |
| 03-PackagesPads | `/api/v2/packages/<package_id>/pads.json` | GET, POST | Получить/создать площадки в пакете | limit, offset | PackagePad |
| 04-Packages | `/api/v2/packages.json` | GET | Получить список пакетов (площадок и форматов) | limit, offset, _id | Package |
| 05-PadsTree | `/api/v2/pads_tree.json` | GET | Получить иерархию площадок (дерево) | _flags | PadsTree |
| 06-ProjectionPrediction | `/api/v2/ad_plans/<ad_plan_id>/projection.json` | POST | Предсказать охват и статистику по таргетингам | ad_plan_id, ad_groups (с таргетингами) | ProjectionPrediction, PredictedRate |
| 07-TargetingsTree | `/api/v2/pads/<pad_id>/targetings_tree.json` | GET | Получить иерархию таргетингов для площадки | pad_id, package_id | TargetingsTree |
| 08-ReadUrls | `/api/v2/urls.json` | GET | Получить список URL-адресов | limit, offset, _id | URL |
| 09-ReadUrl | `/api/v2/urls/<url_id>.json` | GET | Получить информацию об одном URL | url_id | URL |
| 10-CreateUrl | `/api/v2/urls.json` | POST | Создать новый URL (с кодированием в tracking-URL) | url, domain | URL |
| 11-AuditPixelCheck | `/api/v2/audit_pixel/check.json` | POST | Проверить корректность пикселя аудита | url, pixel_type | AuditPixelCheck |
| 12-BannerRemoderation | `/api/v2/banners/<banner_id>/request_moderation.json` | POST | Отправить баннер на переверку модерации | banner_id | Banner |
| 13-BannerFields | `/api/v2/banner_fields.json` | GET | Получить доступные поля баннера для пакета | package_id | BannerField |
| 14-BannerPatterns | `/api/v2/banner_patterns.json` | GET | Получить шаблоны баннеров для пакета | package_id, _ad_group_id | BannerPattern |
| 15-MobileApps | `/api/v2/mobile_apps.json` | GET | Получить список подключённых мобильных приложений | limit, offset, _type | MobileApps |
| 16-SkAdNetworkIdentityShare | `/api/v2/mobile_apps/<app_id>/skan/identity/share.json` | POST | Поделиться SKAdNetwork Identity с партнёром | app_id, partner_id | SkAdNetworkIdentityShare |
| 17-SkAdNetworkIdentityWithdraw | `/api/v2/mobile_apps/<app_id>/skan/identity/withdraw.json` | DELETE | Отозвать SKAdNetwork Identity | app_id, partner_id | - |
| 18-AdPlans | `/api/v2/ad_plans.json` | GET, POST | Получить/создать рекламные кампании | limit, offset, _status, sorting | AdPlan |
| 19-AdPlan | `/api/v2/ad_plans/<ad_plan_id>.json` | GET, POST | Получить/редактировать одну кампанию | ad_plan_id, fields | AdPlan |
| 20-AdGroup | `/api/v2/ad_groups/<ad_group_id>.json` | GET, POST, DELETE | Получить/редактировать/удалить группу объявлений | ad_group_id, package_id | AdGroup |
| 21-AdGroups | `/api/v2/ad_groups.json` | GET, POST | Получить/создать группы объявлений | limit, offset, _ad_plan_id | AdGroup |
| 22-Banner | `/api/v2/banners/<banner_id>.json` | GET, POST, DELETE | Получить/редактировать/удалить баннер | banner_id | Banner |
| 23-Banners | `/api/v2/banners.json` | GET | Получить список баннеров | limit, offset, _ad_group_id, _status | Banner |
| 24-OfferBatchTaskCreate | `/api/v2/remarketing/pricelists/<pricelist_id>/batch.json` | POST, GET | Создать пакетную задачу обновления товаров (NDJSON) | pricelist_id, method (PUT/DELETE) | OfferBatchTask |
| 25-OfferBatchTaskDetail | `/api/v2/remarketing/pricelists/<pricelist_id>/batch/<task_id>.json` | GET | Получить детальный отчёт о пакетной задаче | pricelist_id, task_id | OfferBatchTask |
| 26-AdGroupMassAction | `/api/v2/ad_groups/mass_action.json` | POST | Массово обновить статусы групп объявлений (max 200) | id, status | AdGroupMassAction |
| 27-AdPlanMassAction | `/api/v2/ad_plans/mass_action.json` | POST | Массово обновить статусы кампаний (max 200) | id, status | AdPlanMassAction |

---

### 4. АУДИТОРИИ (20 эндпоинтов)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-RemarketingCounters | `/api/v2/remarketing/counters.json` | GET, POST | Получить/добавить счетчики Top@Mail.ru | _counter_id, _domain, counter_id | RemarketingCounter |
| 02-RemarketingCounter | `/api/v2/remarketing/counters/<counter_id>.json` | GET, POST, DELETE | Управлять счетчиком Top@Mail.ru | counter_id | RemarketingCounter |
| 03-CounterGoals | `/api/v2/remarketing/counters/<counter_id>/goals.json` | GET, POST | Получить/создать цели в счетчике | counter_id, goal_id | CounterGoal |
| 04-CounterGoal | `/api/v2/remarketing/counters/<counter_id>/goals/<goal_id>.json` | GET, POST, DELETE | Управлять целью счетчика | counter_id, goal_id | CounterGoal |
| 05-Goals | `/api/v2/remarketing/goals.json` | GET | Получить список целей (всех счетчиков) | limit, offset | Goal |
| 06-LocalGeos | `/api/v2/local_geos.json` | GET, POST | Получить/создать локальные геолокации | limit, offset | LocalGeo |
| 07-LocalGeo | `/api/v2/local_geos/<local_geo_id>.json` | GET, POST, DELETE | Управлять локальной геолокацией | local_geo_id | LocalGeo |
| 08-RemarketingOfflineGoals | `/api/v2/remarketing/offline_goals.json` | GET, POST | Получить/создать оффлайн-цели | limit, offset | RemarketingOfflineGoal |
| 09-RemarketingOfflineGoal | `/api/v2/remarketing/offline_goals/<offline_goal_id>.json` | GET, POST, DELETE | Управлять оффлайн-целью | offline_goal_id | RemarketingOfflineGoal |
| 10-RemarketingInAppEvents | `/api/v2/remarketing/inapp_events.json` | GET, POST | Получить/создать события в приложении | limit, offset | RemarketingInAppEvent |
| 11-RemarketingUsersList | `/api/v2/remarketing/user_lists/<user_list_id>.json` | GET, POST, DELETE | Управлять списком пользователей | user_list_id | RemarketingUsersList |
| 12-RemarketingUsersLists | `/api/v2/remarketing/user_lists.json` | GET, POST | Получить/создать списки пользователей | limit, offset | RemarketingUsersList |
| 13-SegmentRelations | `/api/v2/remarketing/segments/<segment_id>/relations.json` | GET, POST | Получить/добавить отношения в сегмент | segment_id | SegmentRelation |
| 14-SegmentRelation | `/api/v2/remarketing/segments/<segment_id>/relations/<relation_id>.json` | GET, POST, DELETE | Управлять отношением в сегменте | segment_id, relation_id | SegmentRelation |
| 15-SegmentRelationsDelete | `/api/v2/remarketing/segments/<segment_id>/relations.json` | DELETE | Удалить отношения из сегмента (bulk) | segment_id, relation_id | - |
| 16-Segments | `/api/v2/remarketing/segments.json` | GET, POST | Получить/создать сегменты аудитории | limit, offset, _id, _name | Segment |
| 17-Segment | `/api/v2/remarketing/segments/<id>.json` | GET, POST, DELETE | Получить/редактировать/удалить сегмент | id, pass_condition | Segment |
| 18-SharingKeyUser | `/api/v2/sharing_keys/<sharing_key_id>/users.json` | GET, POST | Получить/добавить пользователей к ключу шаринга | sharing_key_id | SharingKeyUser |
| 19-SharingKey | `/api/v2/sharing_keys/<sharing_key_id>.json` | GET, POST, DELETE | Управлять ключом шаринга (для расшаривания аудиторий) | sharing_key_id | SharingKey |
| 20-InAppEvent | `/api/v2/inapp_events/<inapp_event_id>.json` | GET, POST, DELETE | Управлять событием в приложении | inapp_event_id | InAppEvent |

---

### 5. ФИНАНСЫ (2 эндпоинта)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-TransactionGroups | `/api/v2/billing/transaction_groups.json` | GET | Получить группы транзакций пользователя (с фильтрацией/сортировкой) | limit, offset, фильтры по всем полям | TransactionGroup |
| 02-Transaction | `/api/v2/billing/transactions/<mode>/<user_id>.json` | POST | Перевести средства между агентством и клиентом | mode (to/from), user_id, amount | Transaction |

---

### 6. ЛИД-ФОРМЫ (9 эндпоинтов)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-LeadForm | `/api/v1/lead_ads/lead_forms/<lead_form_id>.json` | GET, POST | Получить/редактировать одну лид-форму | lead_form_id, contact_fields, result_info | LeadForm |
| 02-LeadForms | `/api/v1/lead_ads/lead_forms.json` | GET, POST | Получить список/создать лид-форму | limit, offset, q, _ad_plan_ids, _ad_group_ids | LeadFormsListElement |
| 03-LeadFormArchivation | `/api/v1/lead_ads/lead_forms/<lead_form_id>/archive.json` | POST | Архивировать лид-форму | lead_form_id | - |
| 04-LeadFormUnarchivation | `/api/v1/lead_ads/lead_forms/<lead_form_id>/unarchive.json` | POST | Разархивировать лид-форму | lead_form_id | - |
| 05-LeadFormLeadsExport | `/api/v1/lead_ads/lead_forms/<lead_form_id>/leads/export.json` | POST | Экспортировать лиды из формы (CSV/JSON) | lead_form_id, export_format | LeadsListElement |
| 06-LeadFormImage | `/api/v1/lead_ads/lead_forms/upload_image.json` | POST | Загрузить изображение для лид-формы | file (multipart) | LeadForm |
| 07-Leads | `/api/v1/lead_ads/lead_forms/<lead_form_id>/leads.json` | GET | Получить лиды из лид-формы (с пагинацией) | lead_form_id, limit, offset | LeadsListElement |
| 08-TestLeadSending | `/api/v1/lead_ads/lead_forms/<lead_form_id>/test_lead.json` | POST | Отправить тестовый лид | lead_form_id, contact_info, answers | - |
| 09-LeadFormCopy | `/api/v1/lead_ads/lead_forms/<lead_form_id>/copy.json` | POST | Скопировать лид-форму | lead_form_id | LeadForm |

---

### 7. ПОДПИСКИ (2 эндпоинта)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-Subscriptions | `/api/v3/subscription.json` | GET, POST | Получить/создать подписки на уведомления | resource (BANNER/CAMPAIGN/LEAD), callback_url | Subscription |
| 02-Subscription | `/api/v3/subscription/<subscription_id>.json` | DELETE | Удалить подписку | subscription_id | - |

---

### 8. ОПРОСЫ (7 эндпоинтов)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-Surveys | `/api/v1/lead_ads/survey_forms.json` | GET, POST | Получить/создать опросы | limit, offset, q, _ad_plan_ids, _ad_group_ids | SurveysListElement |
| 02-Survey | `/api/v1/lead_ads/survey_forms/<survey_id>.json` | GET, POST | Получить/редактировать опрос | survey_id, pages, result_info, logo_id | Survey |
| 03-SurveyArchivation | `/api/v1/lead_ads/survey_forms/<survey_id>/archive.json` | POST | Архивировать опрос | survey_id | - |
| 04-SurveyUnarchivation | `/api/v1/lead_ads/survey_forms/<survey_id>/unarchive.json` | POST | Разархивировать опрос | survey_id | - |
| 05-SurveyRespondentsExport | `/api/v1/lead_ads/survey_forms/<survey_id>/respondents/export.json` | POST | Экспортировать ответы респондентов | survey_id, export_format | RespondentsListElement |
| 06-Respondents | `/api/v1/lead_ads/survey_forms/<survey_id>/respondents.json` | GET | Получить ответы респондентов | survey_id, limit, offset | RespondentsListElement |
| 07-SurveyCopy | `/api/v1/lead_ads/survey_forms/<survey_id>/copy.json` | POST | Скопировать опрос | survey_id | Survey |

---

### 9. ОРД ДЛЯ ПАРТНЕРОВ (6 эндпоинтов)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-OrdPartnerPad | `/api/v2/ord/partner_pads/<pad_id>.json` | GET, POST | Получить/обновить ОРД данные площадки партнёра | pad_id | OrdPartnerPad |
| 02-OrdPartnerPads | `/api/v2/ord/partner_pads.json` | GET | Получить ОРД данные всех площадок партнёра | limit, offset | OrdPartnerPad |
| 03-OrdPartnerActStatByPadId | `/api/v2/ord/partner_act_stat/<pad_id>.json` | GET | Получить статистику актов по площадке | pad_id, date_from, date_to | OrdPartnerActStat |
| 04-OrdPartnerActStat | `/api/v2/ord/partner_act_stat.json` | GET | Получить статистику актов партнёра (все площадки) | date_from, date_to, limit, offset | OrdPartnerActStat |
| 05-OrdPartnerSubAgents | `/api/v2/ord/partner_sub_agents.json` | GET, POST | Получить/создать подрядчиков партнёра | limit, offset, sub_agent_id | OrdPartnerSubAgent |
| 06-OrdPartnerSubAgent | `/api/v2/ord/partner_sub_agents/<sub_agent_id>.json` | GET, POST, DELETE | Управлять подрядчиком партнёра | sub_agent_id | OrdPartnerSubAgent |

---

### 10. ОРД АКТЫ АГЕНТСТВ (4 эндпоинта)

| Файл | Эндпоинт | Методы | Что делает | Ключевые параметры | Ссылочные объекты |
|------|----------|--------|-----------|-------------------|-------------------|
| 01-OrdAgencyActs | `/api/v2/ord/agency_acts.json` | GET | Получить акты агентства (с пагинацией/фильтрацией) | limit, offset, date_from, date_to | OrdAgencyAct |
| 02-OrdAgencyAct | `/api/v2/ord/agency_acts/<act_id>.json` | GET | Получить данные одного акта | act_id | OrdAgencyAct |
| 03-OrdAgencyReport | `/api/v2/ord/agency_report.json` | GET | Получить отчет по актам агентства (с агрегацией) | date_from, date_to | OrdAgencyReport |
| 04-OrdAgencyStatus | `/api/v2/ord/agency_status.json` | GET | Получить статус ОРД регистрации агентства | - | - |

---
