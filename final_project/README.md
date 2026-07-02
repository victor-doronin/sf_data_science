# Recommendation Service

Дипломный проект: сервис рекомендаций товаров по `visitorid`.

## Данные для обучения

Используются исходные файлы:

- `data/events.csv.zip`: `timestamp`, `visitorid`, `event`, `itemid`, `transactionid`;
- `data/category_tree.csv`: `category_id`, `parent_id`;
- `data/item_properties_part1.csv`, `data/item_properties_part2.csv`: `timestamp`, `itemid`, `property`, `value`.

Основной обучающий сигнал берется из `events`:

- `view` получает вес 1;
- `addtocart` получает вес 3;
- `transaction` получает вес 10.

Для каждого пользователя считаются взвешенные оценки товаров. Если пользователь неизвестен, сервис использует fallback из самых популярных товаров по взвешенному скору.

## Трансформации

1. `timestamp` переводится в дату через `pd.to_datetime(..., unit="ms")`.
2. Для валидации используется разбиение по времени: train до `2015-07-01 23:59:59.999`, test после этой даты.
3. Для оценки берутся пользователи с покупками в test.
4. Для каждого пользователя формируется топ товаров из истории train.
5. Метрика: `Precision@3`.

## Эксперименты

Проверяются модели:

- `popular_transactions`: топ товаров по покупкам;
- `popular_views`: топ товаров по просмотрам;
- `weighted_popularity`: глобальный топ по весам событий;
- `personal_history_weighted`: персональная история пользователя с весами событий;
- `strong_history`: история только по `addtocart` и `transaction`.

Лучший базовый вариант для сервиса: `personal_history_weighted`.

Текущий результат на временной валидации:

| Модель | Precision@3 |
| --- | ---: |
| `popular_transactions` | 0.002093 |
| `popular_views` | 0.000102 |
| `weighted_popularity` | 0.000919 |
| `personal_history_weighted` | 0.006584 |
| `strong_history` | 0.003215 |

Лучшее значение `Precision@3`: **0.006584**.

В анализе свойств товаров первое свойство за пределами топ-20: **`348`**.

## Обучение

```bash
python scripts/train_recommender.py
```

Скрипт создает файл:

```text
artifacts/recommender_artifacts.json
```

## Docker

Сборка образа:

```bash
docker build -t diploma-recommender:latest .
```

Запуск сервиса:

```bash
docker run --rm -p 8000:8000 diploma-recommender:latest
```

Экспорт образа:

```bash
docker save diploma-recommender:latest -o diploma-recommender.tar
```

## API

Проверка состояния:

```bash
curl http://localhost:8000/health
```

Метрики сервиса:

```bash
curl http://localhost:8000/metrics
```

Рекомендации:

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

Некорректный `visitorid`, например строка вместо числа, вернет HTTP 422. Неизвестный пользователь получит рекомендации из fallback-списка.
