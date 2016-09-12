# Copyright (C) 2016 Tóth, László Attila
# Distributed under the terms of GNU <Lesser> General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/

# Checked against https://www.staff.science.uu.nl/~gent0113/easter/easter_text2c.htm
# Christian Feast Days, names used by Hungarian Lutheran Chuch - Magyarországi Evangélikus Egyház

import enum


class SpecialEvents(enum.Enum):
    christmas = 'c'
    new_year = 'n'
    baptism = 'b'
    easter = 'e'
    reformation = 'r'


class Offset(enum.Enum):
    day = 'd'
    sunday = 's'  #   the next/prev sunday


special_events = {
    SpecialEvents.christmas: {
        'code': SpecialEvents.christmas.value,
    },
    SpecialEvents.new_year: {
        'code': SpecialEvents.new_year.value,
    },
    SpecialEvents.baptism: {
        'code': SpecialEvents.baptism.value,
    },
    SpecialEvents.easter: {
        'code': SpecialEvents.easter.value,
    },
    SpecialEvents.reformation: {
        'code': SpecialEvents.reformation.value,
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
        'skip_if_after': [SpecialEvents.new_year, -2, Offset.day]
    },
    {
        'name': 'Óév este',
        'offset': [SpecialEvents.new_year, -1, Offset.day],
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
        'name': 'Böjt 1. vasránapja (invocativ)',
        'offset': [SpecialEvents.easter, -6, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 2. vasránapja (reminscere)',
        'offset': [SpecialEvents.easter, -5, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 3. vasránapja (oculi)',
        'offset': [SpecialEvents.easter, -4, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 4. vasránapja (laetare)',
        'offset': [SpecialEvents.easter, -3, Offset.sunday],
        'optional': False,
    },
    {
        'name': 'Böjt 5. vasránapja (judica)',
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
        'offset': [SpecialEvents.easter, 0, Offset.day],
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
