# SaaS: изоляция, целевая архитектура и клиент AgroTech X

Модели ниже — C2-схемы границ изоляции; общая функциональная часть показана отдельно.

## Схема на клиента

![C2: схемы в общей БД](diagrams/isolation-schema.svg)

[PNG](diagrams/isolation-schema.png) · [PlantUML](diagrams/isolation-schema.puml)

## БД на клиента — выбранная модель

![C2: отдельные БД](diagrams/isolation-database.svg)

[PNG](diagrams/isolation-database.png) · [PlantUML](diagrams/isolation-database.puml)

## Экземпляр на клиента

![C2: отдельные экземпляры](diagrams/isolation-instance.svg)

[PNG](diagrams/isolation-instance.png) · [PlantUML](diagrams/isolation-instance.puml)

## Контекст SaaS

![C1 SaaS](diagrams/c1-saas.svg)

[PNG](diagrams/c1-saas.png) · [PlantUML](diagrams/c1-saas.puml)

## Контейнеры коммерческого контура

![C2 SaaS](diagrams/c2-saas-tobe.svg)

[PNG](diagrams/c2-saas-tobe.png) · [PlantUML](diagrams/c2-saas-tobe.puml)

Этот вид дополняет [C2 центра](../Task2/architecture.md): там раскрыты синхронизация ферм, ИИ и медиасервис, здесь — управление клиентами и коммерция. Каждый контейнер сохраняет то же имя и назначение.

## AgroTech X — компания-клиент с несколькими фермами

![C2 клиента AgroTech X](diagrams/c2-agrotech-client.svg)

[PNG](diagrams/c2-agrotech-client.png) · [PlantUML](diagrams/c2-agrotech-client.puml)

Дежурный работает через локальный терминал даже при потере WAN. Центральный кабинет объединяет независимо собираемые микрофронтенды в общей оболочке: инциденты, оборудование, аналитика и управление SaaS. Границы и выпуск — [ADR 007](../ADR/007-microfrontends.md). Одной БД клиента недостаточно для изоляции: проверяется tenant на всех каналах и в медиа.

## Трассировка

Task5: три модели — первые три C2; итоговые C1/C2 — далее; AgroTech X с фермами — последний вид. Подписки, российский провайдер, scope, dev-портал, самообслуживание, масштабирование и usage — [коммерческая модель](saas-commercial.md). F07–F09, R01, P02, S01 покрываются этими контрактами; фактические SLO проверяются при реализации.
