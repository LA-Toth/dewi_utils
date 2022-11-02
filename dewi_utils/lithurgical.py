# Copyright 2016-2022 Tóth, László Attila
# Distributed under the terms of the Apache License, Version 2.0

# Checked against https://www.staff.science.uu.nl/~gent0113/easter/easter_text2c.htm
# Christian Feast Days, names used by Hungarian Lutheran Chuch - Magyarországi Evangélikus Egyház

import datetime
import enum


def easter_sunday(year: int):
    # Original http://code.activestate.com/recipes/576517-calculate-easter-western-given-a-year/
    # The code is a somewhat simplified version of  https://en.wikipedia.org/wiki/Computus
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1
    return datetime.date(year, month, day)


class SpecialEvents(enum.Enum):
    christmas = 'c'
    new_year = 'n'
    baptism = 'b'
    easter = 'e'
    reformation = 'r'
    next_new_year = 'nn'


class Offset(enum.Enum):
    day = 'd'
    sunday = 's'  #   the next/prev sunday


special_events = {
    SpecialEvents.christmas: {
        'code': SpecialEvents.christmas.value,
        'func': lambda year: datetime.date(year, 12, 25)
    },
    SpecialEvents.new_year: {
        'code': SpecialEvents.new_year.value,
        'func': lambda year: datetime.date(year, 1, 1)
    },
    SpecialEvents.next_new_year: {
        'code': SpecialEvents.next_new_year.value,
        'func': lambda year: datetime.date(year + 1, 1, 1)
    },
    SpecialEvents.baptism: {
        'code': SpecialEvents.baptism.value,
        'func': lambda year: datetime.date(year, 1, 6)
    },
    SpecialEvents.easter: {
        'code': SpecialEvents.easter.value,
        'func': lambda year: easter_sunday(year)
    },
    SpecialEvents.reformation: {
        'code': SpecialEvents.reformation.value,
        'func': lambda year: datetime.date(year, 10, 31)
    },
}

events = [
    {
        'name': 'Advent 1. vasárnapja',
        'offset': [SpecialEvents.christmas, -4, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Advent 2. vasárnapja',
        'offset': [SpecialEvents.christmas, -3, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Advent 3. vasárnapja',
        'offset': [SpecialEvents.christmas, -2, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Advent 4. vasárnapja',
        'offset': [SpecialEvents.christmas, -1, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Karácsony este',
        'offset': [SpecialEvents.christmas, -1, Offset.day],
        'optional': False,
    },
    {
        'name': 'Karácsony ünnepe',
        'offset': [SpecialEvents.christmas, 0, Offset.day],
        'optional': False,
    },
    {
        'name': 'Karácsony 2. napja',
        'offset': [SpecialEvents.christmas, 1, Offset.day],
        'optional': False,
    },
    {
        'name': 'Karácsony utáni vasárnap',
        'offset': [SpecialEvents.christmas, 1, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.next_new_year, -2, Offset.day]
    },
    {
        'name': 'Óév este',
        'offset': [SpecialEvents.next_new_year, -1, Offset.day],
        'optional': False,
    },
    {
        'name': 'Újév',
        'offset': [SpecialEvents.new_year, 0, Offset.day],
        'optional': False,
    },
    {
        'name': 'Újév utáni vasárnap',
        'offset': [SpecialEvents.new_year, 1, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.baptism, -1, Offset.day]
    },
    {
        'name': 'Vízkereszt ünnepe',
        'offset': [SpecialEvents.baptism, 0, Offset.day],
        'optional': False,
    },
    {
        'name': 'Vízkereszt utáni 1. vasárnap',
        'offset': [SpecialEvents.baptism, 1, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.easter, -1, Offset.sunday]
    },
    {
        'name': 'Vízkereszt utáni 2. vasárnap',
        'offset': [SpecialEvents.baptism, 2, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.easter, -11, Offset.sunday]
    },
    {
        'name': 'Vízkereszt utáni 3. vasárnap',
        'offset': [SpecialEvents.baptism, 3, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.easter, -11, Offset.sunday]
    },
    {
        'name': 'Vízkereszt utáni 4. vasárnap',
        'offset': [SpecialEvents.baptism, 4, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.easter, -11, Offset.sunday]
    },
    {
        'name': 'Vízkereszt utáni 5. vasárnap',
        'offset': [SpecialEvents.baptism, 5, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.easter, -11, Offset.sunday]
    },
    {
        'name': 'Vízkereszt utáni utolsó vasárnap',
        'offset': [SpecialEvents.easter, -10, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Hetvened vasárnap',
        'offset': [SpecialEvents.easter, -9, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Hatvanad vasárnap',
        'offset': [SpecialEvents.easter, -8, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Ötvened vasárnap (esto mihi)',
        'offset': [SpecialEvents.easter, -7, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 1. vasárnapja (invocativ)',
        'offset': [SpecialEvents.easter, -6, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 2. vasárnapja (reminscere)',
        'offset': [SpecialEvents.easter, -5, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 3. vasárnapja (oculi)',
        'offset': [SpecialEvents.easter, -4, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 4. vasárnapja (laetare)',
        'offset': [SpecialEvents.easter, -3, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 5. vasárnapja (judica)',
        'offset': [SpecialEvents.easter, -2, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 6. vasárnapja (palmarum, virágvasárnap)',
        'offset': [SpecialEvents.easter, -1, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Nagycsütörtök',
        'offset': [SpecialEvents.easter, -3, Offset.day],
        'optional': False,
    },
    {
        'name': 'Nagypéntek',
        'offset': [SpecialEvents.easter, -2, Offset.day],
        'optional': False,
    },
    {
        'name': 'Nagyszombat',
        'offset': [SpecialEvents.easter, -1, Offset.day],
        'optional': False,
    },
    {
        'name': 'Húsvét ünnepe',
        'offset': [SpecialEvents.easter, 0, Offset.day],
        'optional': False,
    },
    {
        'name': 'Húsvét 2. napja',
        'offset': [SpecialEvents.easter, 1, Offset.day],
        'optional': False,
    },
    {
        'name': 'Húsvét ünnepe utáni 1. vasárnap (quasi modo geniti)',
        'offset': [SpecialEvents.easter, 1, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Húsvét ünnepe utáni 2. vasárnap (misericordia domini)',
        'offset': [SpecialEvents.easter, 2, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Húsvét ünnepe utáni 3. vasárnap (jubilate)',
        'offset': [SpecialEvents.easter, 3, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Húsvét ünnepe utáni 4. vasárnap (cantate)',
        'offset': [SpecialEvents.easter, 4, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Húsvét ünnepe utáni 5. vasárnap (rogate)',
        'offset': [SpecialEvents.easter, 5, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Mennybemenetel ünnepe',
        'offset': [SpecialEvents.easter, 39, Offset.day],
        'optional': False,
    },
    {
        'name': 'Húsvét ünnepe utáni 6. vasárnap (exaudi)',
        'offset': [SpecialEvents.easter, 6, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Pünkösd ünnepe',
        'offset': [SpecialEvents.easter, 7, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Pünkösd 2. napja',
        'offset': [SpecialEvents.easter, 50, Offset.day],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe',
        'offset': [SpecialEvents.easter, 8, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 1. vasárnap',
        'offset': [SpecialEvents.easter, 9, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 2. vasárnap',
        'offset': [SpecialEvents.easter, 10, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 3. vasárnap',
        'offset': [SpecialEvents.easter, 11, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 4. vasárnap',
        'offset': [SpecialEvents.easter, 12, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 5. vasárnap',
        'offset': [SpecialEvents.easter, 13, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 6. vasárnap',
        'offset': [SpecialEvents.easter, 14, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 7. vasárnap',
        'offset': [SpecialEvents.easter, 15, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 8. vasárnap',
        'offset': [SpecialEvents.easter, 16, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 9. vasárnap',
        'offset': [SpecialEvents.easter, 17, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 10. vasárnap',
        'offset': [SpecialEvents.easter, 18, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 11. vasárnap',
        'offset': [SpecialEvents.easter, 19, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 12. vasárnap',
        'offset': [SpecialEvents.easter, 20, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 13. vasárnap',
        'offset': [SpecialEvents.easter, 21, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 14. vasárnap',
        'offset': [SpecialEvents.easter, 22, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 15. vasárnap',
        'offset': [SpecialEvents.easter, 23, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 16. vasárnap',
        'offset': [SpecialEvents.easter, 24, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 17. vasárnap',
        'offset': [SpecialEvents.easter, 25, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 18. vasárnap',
        'offset': [SpecialEvents.easter, 26, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni 19. vasárnap',
        'offset': [SpecialEvents.easter, 27, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.christmas, -8, Offset.sunday],
    },
    {
        'name': 'Szentháromság ünnepe utáni 20. vasárnap',
        'offset': [SpecialEvents.easter, 28, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.christmas, -8, Offset.sunday],
    },
    {
        'name': 'Szentháromság ünnepe utáni 21. vasárnap',
        'offset': [SpecialEvents.easter, 29, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.christmas, -8, Offset.sunday],
    },
    {
        'name': 'Szentháromság ünnepe utáni 22. vasárnap',
        'offset': [SpecialEvents.easter, 30, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.christmas, -8, Offset.sunday],
    },
    {
        'name': 'Szentháromság ünnepe utáni 23. vasárnap',
        'offset': [SpecialEvents.easter, 31, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.christmas, -8, Offset.sunday],
    },
    {
        'name': 'Szentháromság ünnepe utáni 24. vasárnap',
        'offset': [SpecialEvents.easter, 32, Offset.sunday],
        'optional': True,
        'skip_if_after': [SpecialEvents.christmas, -8, Offset.sunday],
    },
    {
        'name': 'Szentháromság ünnepe utáni utolsó előttit megelőző (ítélet) vasárnap',
        'offset': [SpecialEvents.christmas, -7, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utáni utolsó előtti (reménység) vasárnap',
        'offset': [SpecialEvents.christmas, -6, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Szentháromság ünnepe utolsó (örök élet) vasárnap',
        'offset': [SpecialEvents.christmas, -5, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'A reformáció ünnepe',
        'offset': [SpecialEvents.reformation, 0, Offset.day],
        'optional': False,
    },
]


def print_id_name():
    i = 1
    for e in events:
        print("{:2d} - {}".format(i, e['name']))
        i += 1


def get_special_events_of_year(year: int) -> dict[SpecialEvents, datetime.date]:
    result = dict()
    for s in special_events:
        result[s] = special_events[s]['func'](year)

    return result


def _calculate_day(special_events_of_the_year: dict[SpecialEvents, datetime.date],
                   base_event: SpecialEvents,
                   offset: int,
                   offset_type: Offset) -> datetime.date:
    d: datetime.date = special_events_of_the_year[base_event]

    if offset == 0:
        return d

    if offset_type == Offset.day:
        return d + datetime.timedelta(offset)
    else:  # Offset.sunday
        wd = d.isoweekday() % 7
        if wd:
            # Current date is in Monday..Saturday range
            # Go to previous Sunday
            d = d - datetime.timedelta(wd)
            # If offset is negative, we must remove one Sunday from the offset
            if offset < 0:
                offset += 1
        return d + datetime.timedelta(offset * 7)


def get_events_of_year(year: int) -> list[tuple[str, datetime.date]]:
    result = list()
    specials = get_special_events_of_year(year)
    for e in events:
        d = _calculate_day(specials, *e['offset'])

        if e['optional']:
            other = _calculate_day(specials, *e['skip_if_after'])
            if other >= d:
                result.append((e['name'], d))
        else:
            result.append((e['name'], d))

    return sorted(result, key=lambda x: x[1])


def print_events_of_year(year: int):
    for i in get_events_of_year(year):
        print('{} - {}'.format(i[1].strftime('%Y-%m-%d'), i[0]))
