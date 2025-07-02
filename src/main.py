"""
Модуль для парсинга и представления данных из XML-файла.
Содержит классы для сущностей — узлов XML
и функции для преобразования XML-элементов в объекты Python.
"""

import gzip
import os
import xml.etree.ElementTree as ET
from pprint import pprint

from address_parser import parse_address

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(
    BASE_DIR,
    '..',
    'СКБ_INTEGRA_Тестовое_задание_(1)',
    'ExtrajudicialData.xml.gz',
)


def get_text(elem, tag):
    """
    Получить текстовое значение подэлемента по тегу.
    :param elem: XML-элемент
    :param tag: имя тега
    :return: текстовое значение или None
    """
    return elem.findtext(tag) if elem is not None else None


def get_list(elem, tag, cls):
    """
    Получить список объектов cls (узла XML)
    из всех подэлементов с заданным тегом.
    :param elem: XML-элемент
    :param tag: имя тега
    :param cls: класс для создания объектов (узел XML)
    :return: список объектов cls
    """
    result = []
    if elem is not None:
        for child in elem.findall(tag):
            result.append(cls(child))
    return result


class Publisher:
    """
    Класс для хранения информации об источнике сообщения.
    """

    def __init__(self, elem):
        self.name = get_text(elem, 'Name')
        self.inn = get_text(elem, 'Inn')
        self.ogrn = get_text(elem, 'Ogrn')

    def to_dict(self):
        return {
            'name': self.name,
            'inn': self.inn,
            'ogrn': self.ogrn,
        }


class Debtor:
    """
    Класс для хранения информации о должнике.
    """

    def __init__(self, elem):
        self.name = get_text(elem, 'Name')
        self.birth_date = get_text(elem, 'BirthDate')
        self.birth_place = get_text(elem, 'BirthPlace')
        self.address = get_text(elem, 'Address')
        self.inn = get_text(elem, 'Inn')
        self.previous_names = []
        names_elem = elem.find('NameHistory')
        if names_elem is not None:
            self.previous_names = [
                name.findtext('Value')
                for name in names_elem.findall('PreviousName')
                if name.findtext('Value') is not None
            ]
        self.parsed_address = parse_address(self.address)
        parsed_address = parse_address(self.address)
        self.postal_code = parsed_address.get('postal_code')
        self.region = parsed_address.get('region')
        self.district = parsed_address.get('district')
        self.locality = parsed_address.get('locality')
        self.street = parsed_address.get('street')
        self.house = parsed_address.get('house')
        self.flat = parsed_address.get('flat')

    def to_dict(self):
        return {
            'name': self.name,
            'birth_date': self.birth_date,
            'birth_place': self.birth_place,
            'address': self.address,
            'postal_code': self.postal_code,
            'region': self.region,
            'locality': self.locality,
            'district': self.district,
            'street': self.street,
            'house': self.house,
            'flat': self.flat,
            'inn': self.inn,
            'previous_names': self.previous_names,
        }


class Bank:
    """
    Класс для хранения информации о банке.
    """

    def __init__(self, elem):
        self.name = get_text(elem, 'Name')
        self.bik = get_text(elem, 'Bik')

    def to_dict(self):
        return {
            'name': self.name,
            'bik': self.bik,
        }


class ObligatoryPayment:
    """
    Класс для хранения информации об обязательном платеже.
    """

    def __init__(self, elem):
        self.name = get_text(elem, 'Name')
        self.payment_sum = float(get_text(elem, 'Sum') or 0)

    def to_dict(self):
        return {
            'name': self.name,
            'payment_sum': self.payment_sum,
        }


class MonetaryObligation:
    """
    Класс для хранения информации о денежном обязательстве.
    """

    def __init__(self, elem):
        self.creditor_name = get_text(elem, 'CreditorName')
        self.content = get_text(elem, 'Content')
        self.basis = get_text(elem, 'Basis')
        self.total_sum = float(get_text(elem, 'TotalSum') or 0)
        self.debt_sum = float(get_text(elem, 'DebtSum') or 0)

    def to_dict(self):
        return {
            'creditor_name': self.creditor_name,
            'content': self.content,
            'basis': self.basis,
            'total_sum': self.total_sum,
            'debt_sum': self.debt_sum,
        }


class CreditorsFromEntrepreneurship:
    """
    Класс для хранения информации о кредиторах
    по предпринимательской деятельности.
    """

    def __init__(self, elem):
        payments_elem = elem.find('ObligatoryPayments')
        self.obligatory_payments = get_list(
            payments_elem, 'ObligatoryPayment', ObligatoryPayment
        )

    def to_dict(self):
        return {
            'obligatory_payments': [
                op.to_dict() for op in self.obligatory_payments
            ],
        }


class CreditorsNonFromEntrepreneurship:
    """
    Класс для хранения информации о кредиторах
    не по предпринимательской деятельности.
    """

    def __init__(self, elem):
        payments_elem = elem.find('ObligatoryPayments')
        self.obligatory_payments = get_list(
            payments_elem, 'ObligatoryPayment', ObligatoryPayment
        )
        obligations_elem = elem.find('MonetaryObligations')
        self.monetary_obligations = get_list(
            obligations_elem, 'MonetaryObligation', MonetaryObligation
        )

    def to_dict(self):
        return {
            'obligatory_payments': [
                op.to_dict() for op in self.obligatory_payments
            ],
            'monetary_obligations': [
                mo.to_dict() for mo in self.monetary_obligations
            ],
        }


class ExtrajudicialBankruptcyMessage:
    """
    Класс для хранения информации о сообщении
    о внесудебном банкротстве.
    """

    def __init__(self, elem):
        self.id = get_text(elem, 'Id')
        self.number = get_text(elem, 'Number')
        self.type = get_text(elem, 'Type')
        self.publish_date = get_text(elem, 'PublishDate')
        self.finish_reason = get_text(elem, 'FinishReason')

        # Должник
        debtor_elem = elem.find('Debtor')
        self.debtor = Debtor(debtor_elem) if debtor_elem is not None else None

        # Источник
        publisher_elem = elem.find('Publisher')
        self.publisher = (
            Publisher(publisher_elem) if publisher_elem is not None else None
        )

        # Банки
        banks_elem = elem.find('Banks')
        self.banks = get_list(banks_elem, 'Bank', Bank)

        # Кредиторы по предпринимательской деятельности
        from_ent = elem.find('CreditorsFromEntrepreneurship')
        self.creditors_from_entrepreneurship = (
            CreditorsFromEntrepreneurship(from_ent)
            if from_ent is not None
            else None
        )

        # Кредиторы не по предпринимательской деятельности
        non_from_ent = elem.find('CreditorsNonFromEntrepreneurship')
        self.creditors_non_from_entrepreneurship = (
            CreditorsNonFromEntrepreneurship(non_from_ent)
            if non_from_ent is not None
            else None
        )

    def to_dict(self):
        """
        Преобразовать объект в словарь
        """
        return {
            'id': self.id,
            'number': self.number,
            'type': self.type,
            'publish_date': self.publish_date,
            'finish_reason': self.finish_reason,
            'debtor': self.debtor.to_dict() if self.debtor else None,
            'publisher': self.publisher.to_dict() if self.publisher else None,
            'banks': [bank.to_dict() for bank in self.banks],
            'creditors_from_entrepreneurship': (
                self.creditors_from_entrepreneurship.to_dict()
                if self.creditors_from_entrepreneurship
                else None
            ),
            'creditors_non_from_entrepreneurship': (
                self.creditors_non_from_entrepreneurship.to_dict()
                if self.creditors_non_from_entrepreneurship
                else None
            ),
        }


def parse_messages(file_path):
    """
    Распарсить XML-файл и вернуть список сообщений о банкротстве
    в виде словарей.
    :param file_path: путь к архиву XML
    :return: список словарей сообщений
    """
    with gzip.open(file_path) as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        messages = []
        for elem in root.findall('ExtrajudicialBankruptcyMessage'):
            msg = ExtrajudicialBankruptcyMessage(elem)
            messages.append(msg.to_dict())
        return messages


if __name__ == '__main__':
    pprint(parse_messages(FILE_PATH))
