# Supplier Selection System

Веб-приложение для поддержки выбора поставщика в логистической задаче. Система сравнивает альтернативы вида **«завод-изготовитель + транспортная компания»**, рассчитывает логистические показатели, фильтрует недопустимые варианты и ранжирует поставщиков методом **TOPSIS**.

Проект подготовлен на основе магистерской работы «Разработка специализированного программного обеспечения по выбору поставщика».

## Возможности

- ввод данных о заказчике, заводах, перевозчиках и глобальных ограничениях;
- импорт данных из CSV, XLSX и XLS;
- автоматическое формирование альтернатив «завод + транспортная компания»;
- расчет недельного объема, веса, количества фур, стоимости, времени доставки и совокупной надежности;
- фильтрация альтернатив по tracking, тарифу, времени доставки и надежности;
- три режима расчета весов критериев: дисперсионный метод, энтропийный метод, AHP;
- ранжирование альтернатив методом TOPSIS по стоимости, времени, надежности и расстоянию;
- итоговый план поставки по каждому продукту;
- опциональная визуализация маршрутов через Yandex Maps API.

## Стек

- Python
- Flask
- Pandas
- HTML / CSS / JavaScript
- Bootstrap
- OpenPyXL

## Структура проекта

```text
supplier-selection-system/
├── app.py
├── supplier_selection/
│   ├── __init__.py
│   ├── calculations.py
│   ├── data.py
│   ├── forms.py
│   └── import_export.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── data/
│   ├── factories_example.csv
│   └── carriers_example.csv
├── docs/
│   ├── GITHUB_UPLOAD.md
│   └── resume_project_description.md
├── tests/
│   └── test_calculations.py
├── screenshots/
│   └── .gitkeep
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── LICENSE
```

## Быстрый запуск

```bash
git clone https://github.com/Danchishen/supplier-selection-system.git
cd supplier-selection-system

python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск:

```bash
python app.py
```

После запуска открой:

```text
http://127.0.0.1:5000
```

## Работа с данными

В приложении можно использовать встроенный пример или загрузить свои таблицы. XLSX-шаблон можно скачать в интерфейсе приложения кнопкой **«Скачать XLSX-шаблон»**.

### Колонки для файла заводов

```text
manufacturer, product, city, address, lat, lon, distance_km, transport_time_days,
weekly_quantity_units, unit_weight_kg, unit_volume_m3, manufacturer_reliability,
purchase_price_per_unit, shipping_window
```

### Колонки для файла перевозчиков

```text
name, base_city, cost_per_km, reliability, tracking, speed_kmh
```

Примеры файлов находятся в папке `data/`.

## Алгоритм работы

1. Пользователь вводит данные о заказчике, заводах, перевозчиках и ограничениях.
2. Система формирует все связки «завод + транспортная компания».
3. Для каждой альтернативы рассчитываются стоимость, время доставки, расстояние, объем, вес, количество фур и совокупная надежность.
4. Недопустимые альтернативы исключаются по ограничениям.
5. Веса критериев рассчитываются выбранным методом: дисперсия, энтропия или AHP.
6. Допустимые альтернативы ранжируются методом TOPSIS.
7. Для каждого продукта выбирается лучшая альтернатива и формируется итоговый план поставки.

## Yandex Maps API

Карта маршрутов является опциональной. Чтобы включить ее, создай файл `.env` или задай переменную окружения:

```bash
YANDEX_API_KEY=your_api_key_here
```

Без ключа приложение работает полностью, но вместо карты показывает информационный блок.

## Тесты

```bash
pip install -r requirements-dev.txt
pytest
```

## Автор

Даниил Данчишен
