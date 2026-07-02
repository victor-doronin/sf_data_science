# Recommendation Service

Дипломный проект: сервис рекомендаций товаров по `visitorid` для интернет-магазина.

Ссылка на Docker image:

```text
https://hub.docker.com/r/victordoronin/diploma-recommender
```

## Постановка задачи

Бизнес-задача: разработать рекомендательную систему, чтобы повысить прибыль от допродаж в интернет-магазине на 20%.

Техническая задача: разместить на главной странице сайта рекомендации товаров по идентификатору пользователя в трех местах.

Техническая метрика качества: `Precision@3`.

## Данные для обучения

Используются исходные файлы:

- `events.csv.zip`: лог событий пользователей;
- `category_tree.csv`: дерево категорий товаров;
- `item_properties_part1.csv`, `item_properties_part2.csv`: свойства товаров.

Формат `events`:

| Поле | Описание |
| --- | --- |
| `timestamp` | время события в Unix timestamp, миллисекунды |
| `visitorid` | идентификатор пользователя |
| `event` | тип события: `view`, `addtocart`, `transaction` |
| `itemid` | идентификатор товара |
| `transactionid` | идентификатор транзакции, если была покупка |

Формат `category_tree`:

| Поле | Описание |
| --- | --- |
| `category_id` | идентификатор категории |
| `parent_id` | идентификатор родительской категории |

Формат `item_properties`:

| Поле | Описание |
| --- | --- |
| `timestamp` | момент записи свойства |
| `itemid` | идентификатор товара |
| `property` | название или хеш свойства |
| `value` | значение свойства |

## Трансформации данных

1. `timestamp` переводится в дату через `pd.to_datetime(..., unit="ms")`.
2. Для валидации используется разбиение по времени:
   - train: события до `2015-07-01 23:59:59.999`;
   - test: события после этой даты.
3. Целевым действием для оценки считаются покупки: `event == "transaction"`.
4. Для обучения каждому событию назначается вес:
   - `view`: 1;
   - `addtocart`: 3;
   - `transaction`: 10.
5. Для каждого пользователя считаются взвешенные оценки товаров.
6. Для неизвестных пользователей используется fallback: глобальный топ товаров по взвешенной популярности.

## Эксперименты

Проверялись несколько простых моделей:

| Модель | Логика | Precision@3 |
| --- | --- | ---: |
| `popular_transactions` | глобальный топ товаров по покупкам | 0.002093 |
| `popular_views` | глобальный топ товаров по просмотрам | 0.000102 |
| `weighted_popularity` | глобальный топ по весам событий | 0.000919 |
| `personal_history_weighted` | персональная история пользователя с весами событий | 0.006584 |
| `strong_history` | история только по `addtocart` и `transaction` | 0.003215 |

Лучшая модель: `personal_history_weighted`.

Итоговое качество на временной валидации: **Precision@3 = 0.006584**.

Дополнительный результат анализа свойств товаров: первое свойство за пределами топ-20 — **`348`**.

## Обучение

Скрипт обучения:

```bash
python scripts/train_recommender.py
```

После запуска создается файл:

```text
artifacts/recommender_artifacts.json
```

В артефакте хранятся:

- рекомендации для известных пользователей;
- fallback-рекомендации для новых пользователей;
- результаты экспериментов;
- значение `Precision@3`.

## Docker

Готовый образ опубликован на Docker Hub:

```text
https://hub.docker.com/r/victordoronin/diploma-recommender
```

Скачать образ:

```bash
docker pull victordoronin/diploma-recommender:latest
```

Запустить сервис:

```bash
docker run --rm -p 8000:8000 victordoronin/diploma-recommender:latest
```

После запуска API доступно по адресу:

```text
http://localhost:8000
```

Локальная сборка образа из исходников:

```bash
docker build -t diploma-recommender:latest .
```

Экспорт образа в файл:

```bash
docker save diploma-recommender:latest -o diploma-recommender.tar
```

Загрузка экспортированного образа:

```bash
docker load -i diploma-recommender.tar
```

## API сервиса

### Health check

```bash
curl http://localhost:8000/health
```

Пример ответа:

```json
{
  "status": "ok"
}
```

### Метрики

```bash
curl http://localhost:8000/metrics
```

Endpoint возвращает:

- время работы сервиса;
- количество пользователей в артефакте;
- размер fallback-списка;
- значение `Precision@3`;
- тип модели.

### Рекомендации

```bash
curl "http://localhost:8000/recommend/257597?k=3"
```

Пример ответа:

```json
{
  "visitorid": 257597,
  "recommendations": [355908, 461686, 213834],
  "strategy": "personal_history_weighted"
}
```

Параметры:

- `visitorid`: идентификатор пользователя, целое число;
- `k`: количество рекомендаций, от 1 до 20, по умолчанию 3.

Некорректный `visitorid`, например строка вместо числа, возвращает HTTP 422. Неизвестный пользователь получает рекомендации из fallback-списка.

## Устройство сервиса

Сервис реализован на FastAPI.

Основные файлы:

- `app/main.py`: API сервиса;
- `scripts/train_recommender.py`: обучение и расчет метрик;
- `artifacts/recommender_artifacts.json`: сохраненные рекомендации и метрики;
- `Dockerfile`: инструкция сборки Docker-образа;
- `requirements.txt`: зависимости API.
