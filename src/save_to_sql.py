"""
Модуль для сохранения результатов парсинга сообщений о банкротстве
в базу данных MySQL.

Содержит функции для вставки данных по всем сущностям — узлам XML
и основную функцию main для загрузки всех сообщений в базу данных.

Перед использованием необходима созданная база данных (create_tables.sql)
"""

from datetime import datetime

import pymysql

from main import FILE_PATH, parse_messages

# Конфигурация подключения к базе данных MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'BankruptcyMessages',
    'charset': 'utf8mb4',
}


def to_mysql_date(date_str):
    """
    Преобразует строку даты из XML в формат YYYY-MM-DD для MySQL.
    :param date_str: строка даты (может содержать время)
    :return: строка в формате YYYY-MM-DD или None
    """
    if not date_str:
        return None
    try:
        return (
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            .date()
            .isoformat()
        )
    except Exception:
        try:
            return (
                datetime.strptime(date_str[:10], '%Y-%m-%d').date().isoformat()
            )
        except Exception:
            return None


def insert_publisher(cur, publisher):
    if publisher is None:
        return None
    cur.execute(
        'INSERT INTO publisher (name, inn, ogrn) VALUES (%s, %s, %s)',
        (publisher['name'], publisher['inn'], publisher['ogrn']),
    )
    return cur.lastrowid


def insert_debtor(cur, debtor):
    birth_date = to_mysql_date(debtor['birth_date'])
    cur.execute(
        """INSERT INTO Debtor
        (name, birth_date, birth_place, address, postal_code, region, district, locality, street, house, flat, inn)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            debtor['name'],
            birth_date,
            debtor['birth_place'],
            debtor['address'],
            debtor['postal_code'],
            debtor['region'],
            debtor['district'],
            debtor['locality'],
            debtor['street'],
            debtor['house'],
            debtor['flat'],
            debtor['inn'],
        ),
    )
    debtor_id = cur.lastrowid
    for prev_name in debtor['previous_names']:
        cur.execute(
            'INSERT INTO debtor_previous_name (debtor_id, value) VALUES (%s, %s)',
            (debtor_id, prev_name),
        )
    return debtor_id


def insert_bank(cur, bank):
    if bank is None:
        return None
    cur.execute(
        'INSERT INTO Bank (name, bik) VALUES (%s, %s)',
        (bank['name'], bank['bik']),
    )
    return cur.lastrowid


def insert_obligatory_payment(cur, payment):
    cur.execute(
        'INSERT INTO ObligatoryPayment (name, payment_sum) VALUES (%s, %s)',
        (payment['name'], payment['payment_sum']),
    )
    return cur.lastrowid


def insert_monetary_obligation(cur, mo):
    cur.execute(
        'INSERT INTO MonetaryObligation (creditor_name, content, basis, total_sum, debt_sum) VALUES (%s, %s, %s, %s, %s)',
        (
            mo['creditor_name'],
            mo['content'],
            mo['basis'],
            mo['total_sum'],
            mo['debt_sum'],
        ),
    )
    return cur.lastrowid


def insert_creditors_from_entrepreneurship(cur, cfe):
    cur.execute('INSERT INTO creditors_from_entrepreneurship () VALUES ()')
    cfe_id = cur.lastrowid
    for payment in cfe['obligatory_payments']:
        payment_id = insert_obligatory_payment(cur, payment)
        cur.execute(
            'INSERT INTO cfe_obligatory_payment (cfe_id, payment_id) VALUES (%s, %s)',
            (cfe_id, payment_id),
        )
    return cfe_id


def insert_creditors_non_from_entrepreneurship(cur, cne):
    cur.execute('INSERT INTO creditors_non_from_entrepreneurship () VALUES ()')
    cne_id = cur.lastrowid
    for payment in cne['obligatory_payments']:
        payment_id = insert_obligatory_payment(cur, payment)
        cur.execute(
            'INSERT INTO cne_obligatory_payment (cne_id, payment_id) VALUES (%s, %s)',
            (cne_id, payment_id),
        )
    for mo in cne['monetary_obligations']:
        mo_id = insert_monetary_obligation(cur, mo)
        cur.execute(
            'INSERT INTO cne_monetary_obligation (cne_id, mo_id) VALUES (%s, %s)',
            (cne_id, mo_id),
        )
    return cne_id


def get_or_create_publisher(cur, publisher):
    if publisher is None:
        return None
    cur.execute(
        'SELECT id FROM publisher WHERE name=%s AND inn=%s AND ogrn=%s',
        (publisher['name'], publisher['inn'], publisher['ogrn']),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        'INSERT INTO publisher (name, inn, ogrn) VALUES (%s, %s, %s)',
        (publisher['name'], publisher['inn'], publisher['ogrn']),
    )
    return cur.lastrowid


def get_or_create_debtor(cur, debtor):
    birth_date = to_mysql_date(debtor['birth_date'])
    if debtor['inn'] is None:
        cur.execute(
            'SELECT id FROM Debtor WHERE name=%s AND birth_date=%s AND inn IS NULL',
            (debtor['name'], birth_date),
        )
    else:
        cur.execute(
            'SELECT id FROM Debtor WHERE name=%s AND birth_date=%s AND inn=%s',
            (debtor['name'], birth_date, debtor['inn']),
        )
    row = cur.fetchone()
    if row:
        debtor_id = row[0]
    else:
        cur.execute(
            """INSERT INTO Debtor
            (name, birth_date, birth_place, address, postal_code, region, district, locality, street, house, flat, inn)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                debtor['name'],
                birth_date,
                debtor['birth_place'],
                debtor['address'],
                debtor['postal_code'],
                debtor['region'],
                debtor['district'],
                debtor['locality'],
                debtor['street'],
                debtor['house'],
                debtor['flat'],
                debtor['inn'],
            ),
        )
        debtor_id = cur.lastrowid
    # Добавляем предыдущие имена, если их нет
    for prev_name in debtor['previous_names']:
        cur.execute(
            'SELECT id FROM debtor_previous_name WHERE debtor_id=%s AND value=%s',
            (debtor_id, prev_name),
        )
        if not cur.fetchone():
            cur.execute(
                'INSERT INTO debtor_previous_name (debtor_id, value) VALUES (%s, %s)',
                (debtor_id, prev_name),
            )
    return debtor_id


def get_or_create_bank(cur, bank):
    if bank is None:
        return None
    cur.execute(
        'SELECT id FROM Bank WHERE name=%s AND bik=%s',
        (bank['name'], bank['bik']),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        'INSERT INTO Bank (name, bik) VALUES (%s, %s)',
        (bank['name'], bank['bik']),
    )
    return cur.lastrowid


def get_or_create_obligatory_payment(cur, payment):
    cur.execute(
        'SELECT id FROM ObligatoryPayment WHERE name=%s AND payment_sum=%s',
        (payment['name'], payment['payment_sum']),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        'INSERT INTO ObligatoryPayment (name, payment_sum) VALUES (%s, %s)',
        (payment['name'], payment['payment_sum']),
    )
    return cur.lastrowid


def get_or_create_monetary_obligation(cur, mo):
    cur.execute(
        'SELECT id FROM MonetaryObligation WHERE creditor_name=%s AND total_sum=%s AND debt_sum=%s',
        (mo['creditor_name'], mo['total_sum'], mo['debt_sum']),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        'INSERT INTO MonetaryObligation (creditor_name, content, basis, total_sum, debt_sum) VALUES (%s, %s, %s, %s, %s)',
        (
            mo['creditor_name'],
            mo['content'],
            mo['basis'],
            mo['total_sum'],
            mo['debt_sum'],
        ),
    )
    return cur.lastrowid


def get_or_create_creditors_from_entrepreneurship(cur, cfe):
    cur.execute('INSERT INTO creditors_from_entrepreneurship () VALUES ()')
    cfe_id = cur.lastrowid
    for payment in cfe['obligatory_payments']:
        payment_id = get_or_create_obligatory_payment(cur, payment)
        cur.execute(
            'SELECT 1 FROM cfe_obligatory_payment WHERE cfe_id=%s AND payment_id=%s',
            (cfe_id, payment_id),
        )
        if not cur.fetchone():
            cur.execute(
                'INSERT INTO cfe_obligatory_payment (cfe_id, payment_id) VALUES (%s, %s)',
                (cfe_id, payment_id),
            )
    return cfe_id


def get_or_create_creditors_non_from_entrepreneurship(cur, cne):
    cur.execute('INSERT INTO creditors_non_from_entrepreneurship () VALUES ()')
    cne_id = cur.lastrowid
    for payment in cne['obligatory_payments']:
        payment_id = get_or_create_obligatory_payment(cur, payment)
        cur.execute(
            'SELECT 1 FROM cne_obligatory_payment WHERE cne_id=%s AND payment_id=%s',
            (cne_id, payment_id),
        )
        if not cur.fetchone():
            cur.execute(
                'INSERT INTO cne_obligatory_payment (cne_id, payment_id) VALUES (%s, %s)',
                (cne_id, payment_id),
            )
    for mo in cne['monetary_obligations']:
        mo_id = get_or_create_monetary_obligation(cur, mo)
        cur.execute(
            'SELECT 1 FROM cne_monetary_obligation WHERE cne_id=%s AND mo_id=%s',
            (cne_id, mo_id),
        )
        if not cur.fetchone():
            cur.execute(
                'INSERT INTO cne_monetary_obligation (cne_id, mo_id) VALUES (%s, %s)',
                (cne_id, mo_id),
            )
    return cne_id


def insert_messages(cur, msg):
    """
    Вставляет сообщение о банкротстве и связанные с ним сущности в базу данных.
    :param cur: курсор MySQL
    :param msg: словарь с данными сообщения
    :return: id вставленного сообщения
    """
    publisher_id = get_or_create_publisher(cur, msg['publisher'])
    debtor_id = get_or_create_debtor(cur, msg['debtor'])
    publish_date = to_mysql_date(msg['publish_date'])
    # Проверяем, есть ли уже такое сообщение
    cur.execute(
        'SELECT id FROM ExtrajudicialBankruptcyMessage WHERE message_id=%s',
        (msg['id'],),
    )
    row = cur.fetchone()
    if row:
        message_id = row[0]
    else:
        cur.execute(
            """INSERT INTO ExtrajudicialBankruptcyMessage
            (message_id, number, type, publish_date, finish_reason, debtor_id, publisher_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                msg['id'],
                msg['number'],
                msg['type'],
                publish_date,
                msg['finish_reason'],
                debtor_id,
                publisher_id,
            ),
        )
        message_id = cur.lastrowid

    for bank in msg['banks']:
        bank_id = get_or_create_bank(cur, bank)
        cur.execute(
            'SELECT 1 FROM message_bank WHERE message_id=%s AND bank_id=%s',
            (message_id, bank_id),
        )
        if not cur.fetchone():
            cur.execute(
                'INSERT INTO message_bank (message_id, bank_id) VALUES (%s, %s)',
                (message_id, bank_id),
            )
    if msg['creditors_from_entrepreneurship']:
        cfe_id = get_or_create_creditors_from_entrepreneurship(
            cur, msg['creditors_from_entrepreneurship']
        )
        cur.execute(
            'UPDATE ExtrajudicialBankruptcyMessage SET creditors_from_entrepreneurship_id=%s WHERE id=%s',
            (cfe_id, message_id),
        )
    if msg['creditors_non_from_entrepreneurship']:
        cne_id = get_or_create_creditors_non_from_entrepreneurship(
            cur, msg['creditors_non_from_entrepreneurship']
        )
        cur.execute(
            'UPDATE ExtrajudicialBankruptcyMessage SET creditors_non_from_entrepreneurship_id=%s WHERE id=%s',
            (cne_id, message_id),
        )
    return message_id


def main():
    """
    Основная функция для загрузки всех сообщений из XML-файла в базу данных.
    Выводит в терминал количество успешно добавленных сообщений или ошибку.
    """
    results = parse_messages(FILE_PATH)
    conn = pymysql.connect(**DB_CONFIG)
    success = True
    try:
        with conn.cursor() as cur:
            for msg in results:
                try:
                    insert_messages(cur, msg)
                except Exception as e:
                    print(f'Ошибка при добавлении сообщения: {e}')
                    success = False
            if success:
                conn.commit()
                print('Записи успешно добавлены в базу данных.')
            else:
                conn.rollback()
    except Exception as e:
        print(f'Ошибка при работе с базой данных: {e}')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
