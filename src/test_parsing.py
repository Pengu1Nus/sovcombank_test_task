import unittest
from unittest.mock import MagicMock, patch

from main import (
    Debtor,
    ExtrajudicialBankruptcyMessage,
    MonetaryObligation,
    ObligatoryPayment,
)


class TestDebtor(unittest.TestCase):
    @patch(
        'main.parse_address',
        return_value={
            'postal_code': '111',
            'region': 'Region',
            'district': 'District',
            'locality': 'Locality',
            'street': 'Street',
            'house': '1',
            'flat': '2',
        },
    )
    def test_debtor_fields(self, mock_parse_address):
        elem = MagicMock()
        elem.findtext.side_effect = lambda tag: {
            'Name': 'Sasha',
            'BirthDate': '1990-01-01',
            'BirthPlace': 'Place',
            'Address': 'Addr',
            'Inn': '999',
        }.get(tag)
        name_history = MagicMock()
        prev_name = MagicMock()
        prev_name.findtext.return_value = 'Old Name'
        name_history.findall.return_value = [prev_name]
        elem.find.return_value = name_history
        debtor = Debtor(elem)
        self.assertEqual(debtor.name, 'Sasha')
        self.assertEqual(debtor.birth_date, '1990-01-01')
        self.assertEqual(debtor.previous_names, ['Old Name'])
        self.assertEqual(debtor.postal_code, '111')
        self.assertEqual(debtor.region, 'Region')
        self.assertEqual(debtor.district, 'District')
        self.assertEqual(debtor.locality, 'Locality')
        self.assertEqual(debtor.street, 'Street')
        self.assertEqual(debtor.house, '1')
        self.assertEqual(debtor.flat, '2')


class TestObligatoryPayment(unittest.TestCase):
    def test_obligatory_payment_fields(self):
        elem = MagicMock()
        elem.findtext.side_effect = lambda tag: {
            'Name': 'Tax',
            'Sum': '123.45',
        }.get(tag)
        op = ObligatoryPayment(elem)
        self.assertEqual(op.name, 'Tax')
        self.assertEqual(op.payment_sum, 123.45)


class TestMonetaryObligation(unittest.TestCase):
    def test_monetary_obligation_fields(self):
        elem = MagicMock()
        elem.findtext.side_effect = lambda tag: {
            'CreditorName': 'Creditor',
            'Content': 'Loan',
            'Basis': 'Contract',
            'TotalSum': '1000',
            'DebtSum': '200',
        }.get(tag)
        mo = MonetaryObligation(elem)
        self.assertEqual(mo.creditor_name, 'Creditor')
        self.assertEqual(mo.content, 'Loan')
        self.assertEqual(mo.basis, 'Contract')
        self.assertEqual(mo.total_sum, 1000.0)
        self.assertEqual(mo.debt_sum, 200.0)


class TestExtrajudicialBankruptcyMessage(unittest.TestCase):
    @patch('main.Debtor')
    @patch('main.Publisher')
    @patch('main.get_list', return_value=[])
    def test_message_fields(self, mock_get_list, mock_publisher, mock_debtor):
        elem = MagicMock()
        elem.findtext.side_effect = lambda tag: {
            'Id': 'message42',
            'Number': '42',
            'Type': 'TestType',
            'PublishDate': '2025-01-01',
            'FinishReason': 'Done',
        }.get(tag)
        elem.find.side_effect = lambda tag: MagicMock()
        msg = ExtrajudicialBankruptcyMessage(elem)
        d = msg.to_dict()
        self.assertEqual(d['id'], 'message42')
        self.assertEqual(d['number'], '42')
        self.assertEqual(d['type'], 'TestType')
        self.assertEqual(d['publish_date'], '2025-01-01')
        self.assertEqual(d['finish_reason'], 'Done')
        self.assertIsNotNone(d['debtor'])
        self.assertIsNotNone(d['publisher'])
        self.assertIsInstance(d['banks'], list)


if __name__ == '__main__':
    unittest.main()
