# Проверка документации

Требования: Python 3.10+, PlantUML 1.2026.8 и Graphviz в PATH. C4-PlantUML закреплён локально в `diagrams/vendor/c4-plantuml`; сетевые include не нужны.

```sh
python3 -m venv .venv
. .venv/bin/activate
python tools/build.py --docs-only
python tools/verify.py
```

Проверяются состав схем, рендер SVG/PNG, видимые типы блоков, подписи связей, ссылки с точным регистром, равенство ADR-копий и модель размещения при отказах. Сломанные ссылки и размещение с двумя копиями должны отклоняться. Проверки документов не измеряют задержку распознавания и SLA.
