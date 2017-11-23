# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import os
import typing

from yaml.parser import ParserError

import yaml

PRODUCT_LIST_FILE = 'product_list.yml'


class InvalidProductDescription(ValueError):
    pass


class InvalidProductListVersion(ValueError):
    pass


def _load(filename) ->typing.Dict:
    try:
        with open(filename) as f:
            loaded = yaml.load(f.read())
    except ParserError as e:
        print("Unable to parse file " + filename)
        raise InvalidProductDescription(e)

    return loaded


def _verify_version_of_product_list(product_def):
    if '_format' not in product_def:
        product_def['_format'] = 1
    if product_def['_format'] != 1:
        raise InvalidProductListVersion('The product list version should be 1')
    del product_def['_format']


def _verify_version_of_product_definition(loaded_product):
    if '_format' not in loaded_product:
        loaded_product['_format'] = 1
    if loaded_product['_format'] != 1:
        raise InvalidProductListVersion('The product definition version should be 1')
    del loaded_product['_format']


def load_products(path: str) -> typing.Dict[str, typing.Union[str, typing.Dict[str, typing.Any]]]:
    filename = os.path.join(path, PRODUCT_LIST_FILE)
    product_def = _load(filename)
    products = dict()

    _verify_version_of_product_list(product_def)

    for p in product_def:
        pd = dict(product_def[p])
        modules_file = product_def[p]['modules_file']
        if modules_file.startswith('/'):
            modules_file = modules_file[1:]

        modules_file.replace('/', os.path.sep)

        loaded_product = _load(os.path.join(path, modules_file))
        _verify_version_of_product_definition(loaded_product)
        pd.update(loaded_product)

        products[p] = pd

    return products


def load_default_products():
    return load_products(os.path.join(os.path.expanduser('~'), 'dewi', 'products'))
