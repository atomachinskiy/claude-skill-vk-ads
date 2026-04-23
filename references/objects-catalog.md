## ЧАСТЬ 2: ОБЪЕКТЫ (СХЕМЫ)

### ПОЛЬЗОВАТЕЛИ (24 объекта)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-AdditionalClientInfo | AdditionalClientInfo | name, email, phone, address, client_info | AgencyClients, User |
| 02-AdditionalManagerInfo | AdditionalManagerInfo | name, email, phone, organization, position | User |
| 03-AdditionalUserInfo | AdditionalUserInfo | name, email, phone, address, client_info | User |
| 04-AgencyClientsCount | AgencyClientsCount | total, active, inactive, blocked | AgencyClients |
| 05-AgencyManagerClient | AgencyManagerClient | user_id, manager_id, status, access_type | AgencyManagerClient |
| 06-AgencyManager | AgencyManager | id, username, status, first_name, last_name | Agency |
| 07-Agency | Agency | id, username, status, currency, user_type | AgencyClients, ManagerClients |
| 08-ManagerClientInfo | ManagerClientInfo | user_id, manager_id, agency_id, status, access_type | ManagerClients |
| 09-UserManagerClient | UserManagerClient | user_id, manager_id, status, created | ManagerClients |
| 10-Partner | Partner | id, username, status, name, user_type | - |
| 11-UserAccount | UserAccount | id, balance, a_balance, type, currency_balance_hold | User |
| 12-UserAgency | UserAgency | id, username, status, user_type | User |
| 13-UserRegions | UserRegions | allowed, required, required_one_of | User |
| 14-UserClient | UserClient | id, status, access_type, agency_id | - |
| 15-UserManager | UserManager | id, status, agency_id | - |
| 16-NestedUser | NestedUser | id, username, email, status | AgencyClients, ManagerClients |
| 17-MailingType | MailingType | type, email | User |
| 18-UserEmailSettings | UserEmailSettings | type, email | User |
| 19-User | User | id, username, email, status, currency, account, additional_info, mailings, regions, email_settings | User, AgencyClients, ManagerClients |
| 20-OrdSubAgent | OrdSubAgent | user_type, name, inn, contract_number, contract_date, vat | AgencyClients |
| 21-ClientOrdPhysical | ClientOrdPhysical | name, phone, inn, contract_number, contract_date | AgencyClients |
| 22-ClientOrdJuridical | ClientOrdJuridical | name, inn, contract_number, contract_date, vat | AgencyClients |
| 23-AgencyClient | AgencyClient | user_id, status, access_type, is_vkads, user (nested) | AgencyClients, AgencyClient |
| 24-OrdUser | OrdUser | name, phone, inn, foreign_inn, site | OrdUser |

---

### СПРАВОЧНИКИ (12 объектов)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-AppleApp | AppleApp | id, name, type, category_id, title, icon_image | AppleApp |
| 02-GoogleApp | GoogleApp | id, name, type, category_id, title, icon_image | GoogleApp |
| 03-IconImage | IconImage | preview_url, height, width, type, size | AppleApp, GoogleApp |
| 04-InAppEventCategories | InAppEventCategories | id, name, items (array) | InAppEventCategories |
| 05-MobileCategory | MobileCategory | id, name, type, platform | MobileCategory |
| 06-MobileOperationSystem | MobileOperationSystem | id, description, version, os | MobileOperationSystem |
| 07-MobileOperator | MobileOperator | id, name | MobileOperator |
| 08-MobileTypes | MobileTypes | id, description | MobileTypes |
| 09-MobileVendors | MobileVendors | id, description | MobileVendors |
| 10-Region | Region | id, name, parent_id, flags (array) | Region |
| 11-UserGeo | UserGeo | id, name | UserGeo |
| 12-VkGroup | VkGroup | id, name, screen_name, members_count | - |

---

### РЕКЛАМНЫЕ ОБЪЕКТЫ (42 объекта)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-AgeTargeting | AgeTargeting | age_from, age_to | AdGroup, AdPlan |
| 02-AuditPixel | AuditPixel | id, pixel_type, url, adv_id | AdGroup, AdPlan |
| 03-BannerMassAction | BannerMassAction | id, status | BannerMassAction |
| 04-BannerMassReplace | BannerMassReplace | old_banner_id, new_banner_id | Banner (замена) |
| 05-BirthdayTargeting | BirthdayTargeting | month, day | AdGroup |
| 06-BannerContent | BannerContent | content_id, content_variant | Banner |
| 07-ContentVariant | ContentVariant | id, url, width, height, size | Content |
| 08-Content | Content | id, variants (original, thumbnails) | Banner |
| 09-FulltimeTargeting | FulltimeTargeting | hours_from, hours_to | AdGroup |
| 10-GeoTargeting | GeoTargeting | regions (array of region_id) | AdGroup |
| 11-ModerationReason | ModerationReason | reason_code, reason_text | Banner |
| 12-PackagePad | PackagePad | package_id, pad_id, price_per_click | Package |
| 13-Package | Package | id, name, placement_type, pads (array), price_model, country_restrictions | AdGroup, AdPlan |
| 14-PadCategoryTargeting | PadCategoryTargeting | category_id | AdGroup |
| 15-PadsTree | PadsTree | pad_id, name, pads (children array) | PadsTree |
| 16-PricedGoal | PricedGoal | goal_id, price | AdGroup |
| 17-Targetings | Targetings | ad_group_id, items (array of targeting objects) | AdGroup |
| 18-TargetingsTreeElement | TargetingsTreeElement | id, name, type, children (array) | TargetingsTree |
| 19-TargetingsTree | TargetingsTree | pad_id, items (array of elements) | TargetingsTree |
| 20-Textblock | Textblock | header, title, description | BannerContent |
| 21-URL | URL | id, url, utm_params | Banner, ReadUrl |
| 22-Urls | Urls | items (array of URL) | ReadUrls |
| 23-AuditPixelCheck | AuditPixelCheck | status, pixel_type, message | AuditPixelCheck |
| 24-GeneratedAuditPixel | GeneratedAuditPixel | id, url, generated_at | AuditPixelCheck |
| 25-BannerField | BannerField | field_name, required, type, default_value | BannerFields |
| 26-BannerPattern | BannerPattern | id, name, pattern_type, fields (array) | BannerPatterns |
| 27-TargetingsMassAction | TargetingsMassAction | id, object_id, action (update/delete) | AdGroup (таргетинги) |
| 28-AgeTargetingMassAction | AgeTargetingMassAction | id, age_from, age_to (для batch обновления) | AdGroup |
| 29-MobileOperatingSystemsSkAdNetworkTargeting | MobileOperatingSystemsSkAdNetworkTargeting | os_type, ids_list (array) | AdGroup |
| 30-MobileApps | MobileApps | id, name, platform, category_id, icon_url | MobileApps |
| 31-SkAdNetworkIdentityShare | SkAdNetworkIdentityShare | app_id, partner_id, sharing_status | SkAdNetworkIdentityShare |
| 32-SkAdNetworkIdsCounts | SkAdNetworkIdsCounts | app_id, ios_count, android_count | MobileApps |
| 33-AdPlan | AdPlan | id, name, status, date_start, date_end, budget_limit, budget_limit_day, autobidding_mode, objective | AdPlans, AdPlan |
| 34-AdGroup | AdGroup | id, name, status, package_id, ad_plan_id, budget_limit, budget_limit_day, targetings, banners | AdGroups, AdGroup |
| 35-Banner | Banner | id, name, status, ad_group_id, moderation_status, content, urls, audit_pixels | Banners, Banner |
| 36-AdGroupMassAction | AdGroupMassAction | id, status | AdGroupMassAction |
| 37-AdPlanMassAction | AdPlanMassAction | id, status | AdPlanMassAction |
| 38-ProjectionPrediction | ProjectionPrediction | impressions, clicks, ctr, avg_cpc, budget_spent | ProjectionPrediction |
| 39-PredictedRate | PredictedRate | impressions_min, impressions_max, clicks_min, clicks_max | ProjectionPrediction |
| 40-Histogram | Histogram | bins (array) | ProjectionPrediction |
| 41-HistogramBin | HistogramBin | impressions, clicks, budget | Histogram |
| 42-ProjectionTargetings | ProjectionTargetings | targetings (array with predictions) | ProjectionPrediction |

---

### АУДИТОРИИ (28 объектов)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-RemarketingInAppEventCount | RemarketingInAppEventCount | date, count | RemarketingInAppEvent |
| 02-CounterGoal | CounterGoal | id, counter_id, goal_id, name | CounterGoals, CounterGoal |
| 03-RemarketingCounterUser | RemarketingCounterUser | user_id, counter_id, event_type | RemarketingCounter |
| 04-RemarketingCounter | RemarketingCounter | id, counter_id, name, domain, status, working, system_status | RemarketingCounters, RemarketingCounter |
| 05-RemarketingCounterGoal | RemarketingCounterGoal | id, counter_id, goal_id, goal_name | CounterGoals |
| 06-Goal | Goal | id, counter_id, name, created_at | Goals |
| 07-Goals | Goals | items (array of Goal) | Goals |
| 08-InAppEvent | InAppEvent | id, name, event_category | InAppEvent |
| 09-InAppTracker | InAppTracker | id, event_id, description | RemarketingInAppEvent |
| 10-LocalGeoPoint | LocalGeoPoint | latitude, longitude, radius | LocalGeo |
| 11-LocalGeoPointTargeting | LocalGeoPointTargeting | points (array of LocalGeoPoint) | LocalGeo |
| 12-LocalGeoTargeting | LocalGeoTargeting | geo_points, radius_by_default | LocalGeo |
| 13-LocalGeo | LocalGeo | id, name, points (array), created_at | LocalGeos, LocalGeo |
| 14-RemarketingOfflineGoal | RemarketingOfflineGoal | id, name, created_at, updated_at | RemarketingOfflineGoals, RemarketingOfflineGoal |
| 15-RemarketingInAppEvent | RemarketingInAppEvent | id, app_id, event_type, event_category | RemarketingInAppEvents |
| 16-RemarketingPricelistUser | RemarketingPricelistUser | user_id, pricelist_id, event_type | RemarketingUsersList |
| 17-RemarketingUsersListHistory | RemarketingUsersListHistory | user_id, added_at, removed_at | RemarketingUsersList |
| 18-RemarketingUsersListUser | RemarketingUsersListUser | user_id, added_at, vk_id | RemarketingUsersList |
| 19-RemarketingUsersList | RemarketingUsersList | id, name, users_count, created_at, user_ids (array) | RemarketingUsersLists, RemarketingUsersList |
| 20-RemarketingInAppEventCountDate | RemarketingInAppEventCountDate | date, count, timestamp | RemarketingInAppEvent |
| 21-SegmentRelation | SegmentRelation | id, object_type, object_id, params (goal_id, type, counter_id, left, right) | SegmentRelations, SegmentRelation |
| 22-SegmentUser | SegmentUser | user_id, segment_id, added_at | Segment |
| 23-Segment | Segment | id, name, created, updated, pass_condition, relations (array) | Segments, Segment |
| 24-SharingKeySource | SharingKeySource | segment_id, source_user_id | SharingKey |
| 25-SharingKeyUser | SharingKeyUser | user_id, access_type | SharingKeyUser |
| 26-SharingKey | SharingKey | id, segment_id, source_user_id, key_value, shared_users (array) | SharingKeys, SharingKey |
| 27-UserSegment | UserSegment | user_id, segment_id, member | Segment |
| 28-RemarketingPricelist | RemarketingPricelist | id, name, created_at, users_count | OfferBatchTaskCreate |

---

### ЛИД-ФОРМЫ (20 объектов)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-LeadForm | LeadForm | id, name, status, contact_fields, result_info, agreement, notifications, pages | LeadForms, LeadForm |
| 02-LeadFormResultInfo | LeadFormResultInfo | title, description, site_url, phone, cta_text | LeadForm |
| 03-LeadFormAgreementTemplateDocument | LeadFormAgreementTemplateDocument | company_title, registration_address | LeadForm |
| 04-LeadFormAgreement | LeadFormAgreement | usage, template_document | LeadForm |
| 05-LeadFormNotificationDestination | LeadFormNotificationDestination | type, value (email/webhook) | LeadForm |
| 06-LeadFormNotification | LeadFormNotification | destinations (array) | LeadForm |
| 07-LeadFormQuestionAnswer | LeadFormQuestionAnswer | id, text, type | LeadFormQuestion |
| 08-LeadFormQuestion | LeadFormQuestion | id, text, type, is_required, answers (array) | LeadFormBlock |
| 09-LeadFormBlockData | LeadFormBlockData | type, data (variant of content) | LeadFormBlock |
| 10-LeadFormBlock | LeadFormBlock | block_data, block_type | LeadFormPage |
| 11-LeadFormPage | LeadFormPage | blocks (array) | LeadForm |
| 12-LeadFormsListElement | LeadFormsListElement | id, name, status, created, updated, leads_count, ad_plans_count | LeadForms |
| 13-LeadsListElement | LeadsListElement | id, form_id, ad_plan_id, ad_group_id, banner_id, created_at, contact_info, answers | Leads |
| 14-LeadContactInfo | LeadContactInfo | first_name, phone, birth_date, city, email | Lead |
| 15-LeadAnswerOption | LeadAnswerOption | id, text, type | LeadAnswer |
| 16-LeadAnswer | LeadAnswer | question_id, answer_options (array), text | Lead |
| 17-LeadFormPromoCode | LeadFormPromoCode | code, discount_percent, discount_amount | LeadForm |
| 18-LeadFormBonus | LeadFormBonus | bonus_type, value, description | LeadForm |
| 19-LeadFormDiscount | LeadFormDiscount | discount_percent, discount_amount | LeadForm |
| 20-LeadFormAward | LeadFormAward | award_type, award_value | LeadForm |

---

### ОПРОСЫ (17 объектов)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-SurveyConditionAnswerExists | SurveyConditionAnswerExists | question_id, answer_id | SurveyCondition |
| 02-SurveyConditionOr | SurveyConditionOr | conditions (array of condition objects) | SurveyCondition |
| 03-SurveyCondition | SurveyCondition | type (answer_exists, or, and) | Survey |
| 04-SurveyQuestionAnswer | SurveyQuestionAnswer | id, text, type | SurveyQuestion |
| 05-SurveyQuestionScale | SurveyQuestionScale | min_value, max_value, step | SurveyQuestion |
| 06-SurveyQuestion | SurveyQuestion | id, text, type, is_required, answers, scale | SurveyBlock |
| 07-SurveyBlockData | SurveyBlockData | type, data (variant of content) | SurveyBlock |
| 08-SurveyBlock | SurveyBlock | block_data, block_type | SurveyPage |
| 09-SurveyPage | SurveyPage | blocks (array) | Survey |
| 10-SurveyResultInfoPositive | SurveyResultInfoPositive | title, description, site_url, cta_text | SurveyResultInfo |
| 11-SurveyResultInfoNegative | SurveyResultInfoNegative | title, description, site_url, cta_text | SurveyResultInfo |
| 12-SurveyResultInfo | SurveyResultInfo | positive, negative | Survey |
| 13-Survey | Survey | id, name, status, title, description, pages, result_info, logo_id, gradient | Surveys, Survey |
| 14-SurveysListElement | SurveysListElement | id, name, status, created, updated, respondents_count, ad_plans_count | Surveys |
| 15-RespondentAnswerOption | RespondentAnswerOption | id, text | RespondentAnswer |
| 16-RespondentAnswer | RespondentAnswer | question_id, answer_options (array), text | Respondent |
| 17-RespondentsListElement | RespondentsListElement | id, survey_id, ad_plan_id, ad_group_id, banner_id, created_at, answers | Respondents |

---

### ПОДПИСКИ (1 объект)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-Subscription | Subscription | id, resource, callback_url, created_at | Subscriptions |

---

### ФИНАНСЫ (2 объекта)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-TransactionGroup | TransactionGroup | id, amount, date, description, type, tax_amount, receipt | TransactionGroups |
| 02-Transaction | Transaction | amount, created_at, client_balance, agency_balance | Transaction |

---

### ОРД ПАРТНЕРОВ (3 объекта)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-OrdPartnerPad | OrdPartnerPad | pad_id, name, inn, contract_number, contract_date | OrdPartnerPad |
| 02-OrdPartnerActStat | OrdPartnerActStat | date, pad_id, impressions, clicks, spend | OrdPartnerActStat |
| 03-OrdPartnerSubAgent | OrdPartnerSubAgent | id, name, user_type, inn, contract_info | OrdPartnerSubAgents |

---

### ОРД АГЕНТСТВ (3 объекта)

| Файл | Object name | Ключевые поля (топ-5) | Используется в методах |
|------|-------------|----------------------|------------------------|
| 01-OrdAgencyAct | OrdAgencyAct | id, date, period_start, period_end, amount, status | OrdAgencyActs, OrdAgencyAct |
| 02-OrdAgencyReport | OrdAgencyReport | period_start, period_end, total_amount, acts_count | OrdAgencyReport |
| 03-OrdAgencyStatus | OrdAgencyStatus | registration_status, confirmed_at | OrdAgencyStatus |

---
