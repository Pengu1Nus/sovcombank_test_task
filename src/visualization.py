"""
Модуль для визуализации данных
Для обработки данных из БД используется pandas
Для визуализации — matplotlib
"""

from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import pymysql


def load_data():
    """
    Загружает данные о регионе, дате рождения и сумме долга
    из базы данных.
    :return: DataFrame с колонками region, birth_date, debt_sum
    """
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='BankruptcyMessages',
        charset='utf8mb4',
    )
    query = """
    SELECT
        d.region,
        d.birth_date,
        mo.debt_sum
    FROM
        Debtor d
        JOIN ExtrajudicialBankruptcyMessage m ON m.debtor_id = d.id
        LEFT JOIN creditors_non_from_entrepreneurship cne ON m.creditors_non_from_entrepreneurship_id = cne.id
        LEFT JOIN cne_monetary_obligation cne_mo ON cne.id = cne_mo.cne_id
        LEFT JOIN MonetaryObligation mo ON cne_mo.mo_id = mo.id
    WHERE
        mo.debt_sum IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def plot_region_debt(df, save_path=None):
    """
    Строит столбчатую диаграмму по сумме долгов в разрезе регионов.
    Сохраняет график в PNG, если указан save_path, иначе показывает на экране.

    :param df: DataFrame с колонками region и debt_sum
    :param save_path: путь для сохранения PNG-файла (или None)
    """

    # Группируем и сортируем по сумме долгов по регионам
    region_debt = (
        df.groupby('region')['debt_sum'].sum().sort_values(ascending=False)
    )
    region_debt = region_debt[region_debt > 0]
    fig, ax = plt.subplots(figsize=(12, 6))
    region_debt.plot(kind='bar', ax=ax)
    plt.title('Сумма долгов по регионам')
    plt.ylabel('Сумма долга')
    plt.xlabel('Регион')
    plt.xticks(rotation=45, ha='right')

    # Форматируем ось Y в миллионах
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f'{x / 1_000_000:.1f} млн')
    )
    plt.tight_layout()
    if save_path:
        save_plot_to_png(fig, save_path)
    else:
        plt.show()


def plot_age_debt(df, save_path=None):
    """
    Строит круговую диаграмму по сумме долгов в разрезе возрастных групп.
    Сохраняет график в PNG, если указан save_path, иначе показывает на экране.

    :param df: DataFrame с колонками birth_date и debt_sum
    :param save_path: путь для сохранения PNG-файла (или None)
    """

    # Преобразуем дату рождения в возраст
    df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
    df['age'] = df['birth_date'].apply(
        lambda x: datetime.now().year - x.year if pd.notnull(x) else None
    )

    # Формируем возрастные группы по 10 лет
    bins = list(range(10, 100, 10))
    labels = [f'Группа {b} летних' for b in bins]
    df['age_group'] = pd.cut(
        df['age'], bins=bins, labels=labels[:-1], right=False
    )

    # Сумма долгов по возрастным группам
    age_debt = df.groupby('age_group', observed=False)['debt_sum'].sum()
    age_debt = age_debt[age_debt > 0]

    # Количество людей в каждой возрастной группе
    age_counts = df['age_group'].value_counts(sort=False).sort_index()
    age_counts = age_counts.loc[age_debt.index]

    # Подписи для круговой диаграммы "пример — Группа 30 летних (25 чел)"
    pie_labels = [
        f'{group} ({count} чел)'
        for group, count in zip(age_debt.index, age_counts)
    ]

    fig, ax = plt.subplots(figsize=(8, 8))
    age_debt.plot(
        kind='pie',
        labels=pie_labels,
        autopct='%1.1f%%',
        startangle=90,
        ylabel='',
        legend=False,
        ax=ax,
    )
    plt.title(
        'Доля суммы долгов по возрастным группам\n'
        '(в скобках — количество людей)'
    )
    plt.tight_layout()
    if save_path:
        save_plot_to_png(fig, save_path)
    else:
        plt.show()


def save_plot_to_png(fig, filename):
    """
    Сохраняет визуализации в PNG-файл в текущей директории.

    :param fig: matplotlib.figure.Figure
    :param filename: имя файла для сохранения
    """
    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)


def main():
    """
    Основная функция: загружает данные и строит графики
    по регионам и возрастным группам.
    """
    df = load_data()
    plot_region_debt(df, save_path='region_debt.png')
    plot_age_debt(df, save_path='age_debt.png')


if __name__ == '__main__':
    main()
