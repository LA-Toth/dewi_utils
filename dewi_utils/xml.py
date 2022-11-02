# Copyright 2017-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

from xml.etree import ElementTree


def create_dict_from_xml_string(xml: str):
    root = ElementTree.fromstring(xml)
    return create_dict_from_xml_element(root)


def create_dict_from_xml_element(elem: ElementTree):
    return _add_as_dict(elem)


def _add_as_list(elem: ElementTree):
    result = list()
    for child_item in elem:
        if child_item:
            if len(child_item) == 1:
                result.append(_add_as_dict(child_item))
            if len(child_item) > 1:
                if child_item[0].tag != child_item[1].tag:
                    result.append(_add_as_dict(child_item))
                else:
                    result.append(_add_as_list(child_item))
        elif child_item.text:
            text = child_item.text.strip()
            if text:
                result.append(text)
    return result


def _add_as_dict(elem: ElementTree) -> dict | str:
    value = dict()
    if len(list(elem)):
        for child_item in list(elem):
            if child_item.tag in value:
                if not isinstance(value[child_item.tag], list):
                    value[child_item.tag] = [value[child_item.tag]]
                value[child_item.tag].append(_add_as_dict(child_item))
            else:
                value[child_item.tag] = _add_as_dict(child_item)
        if elem.items():
            value['_attrs'] = dict(elem.items())
        if elem.text:
            text = elem.text.strip()
            if text:
                value['text'] = text

    elif elem.items():
        value = dict(_attrs=dict(elem.items()))
        if elem.text:
            text = elem.text.strip()
            if text:
                value['text'] = text

    elif elem.text:
        text = elem.text.strip()
        if text:
            value = text

    return value
