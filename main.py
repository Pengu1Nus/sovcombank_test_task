import gzip
import xml.etree.ElementTree as ET
from pprint import pprint

FILE_PATH = 'СКБ_INTEGRA_Тестовое_задание_(1)/ExtrajudicialData.xml.gz'


def get_text(elem, tag):
    return elem.findtext(tag) if elem is not None else None


def get_list(elem, tag, cls):
    result = []
    if elem is not None:
        for child in elem.findall(tag):
            result.append(cls(child))
    return result


class Publisher:
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

    def to_dict(self):
        return {
            'name': self.name,
            'birth_date': self.birth_date,
            'birth_place': self.birth_place,
            'address': self.address,
            'inn': self.inn,
            'previous_names': self.previous_names,
        }


class Bank:
    def __init__(self, elem):
        self.name = get_text(elem, 'Name')
        self.bik = get_text(elem, 'Bik')

    def to_dict(self):
        return {
            'name': self.name,
            'bik': self.bik,
        }


class ObligatoryPayment:
    def __init__(self, elem):
        self.name = get_text(elem, 'Name')
        self.sum = float(get_text(elem, 'Sum') or 0)

    def to_dict(self):
        return {
            'name': self.name,
            'sum': self.sum,
        }


class MonetaryObligation:
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
    def __init__(self, elem):
        self.id = get_text(elem, 'Id')
        self.number = get_text(elem, 'Number')
        self.type = get_text(elem, 'Type')
        self.publish_date = get_text(elem, 'PublishDate')
        self.finish_reason = get_text(elem, 'FinishReason')

        debtor_elem = elem.find('Debtor')
        self.debtor = Debtor(debtor_elem) if debtor_elem is not None else None

        publisher_elem = elem.find('Publisher')
        self.publisher = (
            Publisher(publisher_elem) if publisher_elem is not None else None
        )

        banks_elem = elem.find('Banks')
        self.banks = get_list(banks_elem, 'Bank', Bank)

        from_ent = elem.find('CreditorsFromEntrepreneurship')
        self.creditors_from_entrepreneurship = (
            CreditorsFromEntrepreneurship(from_ent)
            if from_ent is not None
            else None
        )

        non_from_ent = elem.find('CreditorsNonFromEntrepreneurship')
        self.creditors_non_from_entrepreneurship = (
            CreditorsNonFromEntrepreneurship(non_from_ent)
            if non_from_ent is not None
            else None
        )

    def to_dict(self):
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
    with gzip.open(file_path) as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        messages = []
        for elem in root.findall('ExtrajudicialBankruptcyMessage'):
            msg = ExtrajudicialBankruptcyMessage(elem)
            messages.append(msg.to_dict())
        return messages


if __name__ == '__main__':
    result = parse_messages(FILE_PATH)
    pprint(result)
