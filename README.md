# sovcombank-test-task

## Описание
Решение тестового задания: парсинг XML, загрузка в MySQL, SQL-запросы и визуализация данных о банкротствах физических лиц.

## Требования
- Python 3.11
- MySQL server
- Установленные зависимости из requirements.txt (pandas, matplotlib, pymysql, natasha и др.)


## Структура проекта

- `main.py` — парсинг XML и вывод в терминал
- `save_to_sql.py` — запись данных в MySQL
- `visualization.py` — построение графиков
- `test_parsing.py` — тесты парсинга
- `sql_queries` — директория с SQL запросами

## Важно
**Перед запуском убедитесь, что рядом с папкой `src` находится папка с исходным XML-файлом для парсинга.**
Пример структуры:
```
sovcombank_test_task/
├── src/
│   ├── main.py
│   └── ...
├── СКБ_INTEGRA_Тестовое_задание_(1)/
│   └── ExtrajudicialData.xml.gz
├── requirements.txt
└── README.md
```


## Задание 1
1. Установить виртуальное окружение
    ```bash
    python3 -m venv .venv
    ```
2. Активировать виртуальное окружение
    ```bash
    source .venv/bin/activate
    ```
3. Установить необходимые зависимости
    ```bash
    pip install -r requirements.txt
    ```
4. Перейти в директорию скриптов
    ```bash
    cd src
    ```
5. Запуск теста
    ```bash
    python test_parsing.py
    ```
6. Запустить и вывести в терминал результат парсинга
    ```bash
    python main.py
    ```


### Настройка базы данных и запись в базу

1. Создайте базу данных с именем `BankruptcyMessages` в MySQL.
2. Выполните SQL-скрипт `create_tables.sql` для создания таблиц:
    ```bash
    mysql -u root -p BankruptcyMessages < sql_queries/create_tables.sql
    ```
3. Либо скопируйте данные из create_tables.sql и вручную в MySQL создайте таблицы

4. Запуск скрипта для записи данных в БД

    ```bash
    python save_to_sql.py
    ```


## 2 Задание

1. После успешного добавления данных в БД, выполнить запросы с именами
- first_sql_query.sql
- second_sql_query.sql
- third_sql_query.sql


## 3 задание

1. Для просмотра визуализации данных выполнить скрипт
    ```bash
    python visualization.py
    ```
2. В результате будут созданы файлы `age_debt.png` и `region_debt.png`
