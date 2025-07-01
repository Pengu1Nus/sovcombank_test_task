"""
Модуль для парсинга российских адресов с помощью Natasha.
Результат — словарь с разбитыми по полям компонентами адреса:
индекс, регион, район, населённый пункт, улица, дом, квартира.

Функция parse_address поддерживает основные варианты написания и сокращения
адресов, а также обработки для случаев, когда Natasha не распознаёт компонент.
"""

import re

from natasha import AddrExtractor, MorphVocab

morph_vocab = MorphVocab()
addr_extractor = AddrExtractor(morph_vocab)

# Необходимые для Natasha типы
PART_TYPE_MAP = {
    'индекс': 'postal_code',
    'страна': 'country',
    'регион': 'region',
    'область': 'region',
    'край': 'region',
    'республика': 'region',
    'город': 'city',
    'населенный пункт': 'settlement',
    'улица': 'street',
    'проспект': 'street',
    'микрорайон': 'street',
    'переулок': 'street',
    'шоссе': 'street',
    'площадь': 'street',
    'дом': 'house',
    'корпус': 'block',
    'строение': 'building',
    'квартира': 'flat',
    'офис': 'office',
    'поселок': 'settlement',
    'деревня': 'settlement',
    'село': 'settlement',
    'район': 'district',
    'р-н': 'district',
    'станица': 'settlement',
    'ст.': 'settlement',
}


def parse_address(address):
    """
    Парсинг адресов с фиксированными полями. Возвращает словарь.
    """
    if not address:
        return {
            'raw': None,
            'postal_code': None,
            'region': None,
            'district': None,
            'locality': None,
            'street': None,
            'house': None,
            'flat': None,
        }

    address = re.sub(r'\bгор\.\s*', 'г. ', address, flags=re.IGNORECASE)
    address = re.sub(r'\bр-н\b', 'район', address, flags=re.IGNORECASE)
    address = re.sub(r'\bр-он\b', 'район', address, flags=re.IGNORECASE)
    matches = list(addr_extractor(address))
    result = {
        'raw': address,
        'postal_code': None,
        'region': None,
        'district': None,
        'locality': None,
        'street': None,
        'house': None,
        'flat': None,
    }

    # Основной проход по найденным Natasha компонентам
    for match in matches:
        fact = match.fact
        if not hasattr(fact, 'type') or fact.type is None:
            continue
        key = PART_TYPE_MAP.get(fact.type.lower())
        if key == 'region' and result['region'] is None:
            result['region'] = f'{fact.value} {fact.type}'.strip()
        elif key == 'district' and result['district'] is None:
            result['district'] = f'{fact.value} {fact.type}'.strip()
        elif key == 'street' and result['street'] is None:
            result['street'] = fact.value
        elif key == 'postal_code' and result['postal_code'] is None:
            result['postal_code'] = fact.value
        elif key in ('city', 'settlement') and result['locality'] is None:
            result['locality'] = fact.value
        elif key == 'house' and result['house'] is None:
            result['house'] = fact.value
        elif key == 'flat' and result['flat'] is None:
            result['flat'] = fact.value

    # Обработка специфичных зон как улиц
    if result['street'] is None:
        # Обработка микрорайона как улицы
        mkr_match = re.search(r'мкр\.?\s*\d+[а-яА-Я]?', address, re.IGNORECASE)
        if mkr_match:
            result['street'] = mkr_match.group(0).strip()

        # Обработка для территории (тер.)
        ter_match = re.search(r'тер\.?\s*[^,]+', address, re.IGNORECASE)
        if ter_match:
            result['street'] = ter_match.group(0).strip()

    # Обработка для района (ищем "слово район" после региона)
    if result['district'] is None:
        district_match = re.search(r'([А-Яа-яё\-]+)\s+район', address)
        if district_match:
            result['district'] = f'{district_match.group(1).strip()} район'

    # Обработка для locality (после региона)
    if result['locality'] is None and result['region']:
        region_pattern = re.escape(result['region'])
        locality_match = re.search(region_pattern + r',\s*([^,]+)', address)
        if locality_match:
            candidate = locality_match.group(1).strip()

            # Пропускаем если это район, улица и т.п.
            if not re.search(
                r'(район|р-н|ул\.|улица|мкр\.|микрорайон|просп\.|пер\.|шоссе|пл\.|дом|д\.)',
                candidate,
                re.IGNORECASE,
            ):
                result['locality'] = candidate

    # Обработка если locality всё ещё не найден — ищем после
    # региона или района, а также р.п. и ст.
    if result['locality'] is None:
        # После региона
        if result['region']:
            region_pattern = re.escape(result['region'])
            locality_match = re.search(
                region_pattern + r',\s*([^,]+)', address
            )
            if locality_match:
                candidate = locality_match.group(1).strip()
                if not re.search(
                    r'(район|р-н|ул\.|улица|мкр\.|микрорайон|просп\.|пер\.|шоссе|пл\.|дом|д\.)',
                    candidate,
                    re.IGNORECASE,
                ):
                    result['locality'] = candidate
        # После района
        if result['locality'] is None and result['district']:
            district_pattern = re.escape(result['district'])
            locality_match = re.search(
                district_pattern + r',\s*([^,]+)', address
            )
            if locality_match:
                candidate = locality_match.group(1).strip()
                if not re.search(
                    r'(ул\.|улица|мкр\.|микрорайон|просп\.|пер\.|шоссе|пл\.|дом|д\.)',
                    candidate,
                    re.IGNORECASE,
                ):
                    result['locality'] = candidate
        # р.п. (рабочий поселок) <название>
        if result['locality'] is None:
            rp_match = re.search(
                r'р\.п\.?\s*([А-Яа-яё\- ]+?)(?:,|ул\.|улица|$)', address
            )
            if rp_match:
                result['locality'] = f'р.п. {rp_match.group(1).strip()}'

        # ст. (станица) <название>
        if result['locality'] is None:
            stanica_match = re.search(
                r'ст\.?\s*([А-Яа-яё\- ]+?)(?:,|ул\.|улица|$)', address
            )
            if stanica_match:
                result['locality'] = f'ст. {stanica_match.group(1).strip()}'
    return result
