# Copyright (C) 2017 Laszlo Attila Toth
# Distributed under the terms of GNU General Public License v3
# The license can be found in COPYING file or on http://www.gnu.org/licenses/


import dewi.tests
from dewi.utils.xml import create_dict_from_xml_string


class XmlTest(dewi.tests.TestCase):
    def assert_xml_equals_dict(self, d: dict, xml: str):
        self.assert_equal(d, create_dict_from_xml_string('<?xml version="1.0" encoding="UTF-8"?>' + xml))

    def test_one_child_with_attrs(self):
        self.assert_xml_equals_dict({'xml': {'_attrs': {'a': '42'}}}, '<root_node><xml a="42"/></root_node>')

    def test_empty_root_(self):
        self.assert_xml_equals_dict(dict(), '<root_node/>')

    def test_root_node_has_one_two_children_with_text(self):
        self.assert_xml_equals_dict({'workflow': 'In progress', 'project': 'dewi'},
                                    '<root_node><workflow>In progress</workflow><project>dewi</project></root_node>')

    def test_that_two_children_of_root_with_same_tag_converts_child_to_list(self):
        self.assert_xml_equals_dict({'workflow': ['In progress', 'Done']},
                                    '<root_node><workflow>In progress</workflow><workflow>Done</workflow></root_node>')

    def test_child_of_child_with_attrs_or_text(self):
        self.assert_xml_equals_dict({'parent': {'_attrs': {'a': '34'}, 'child': 'A text'}},
                                    '<root_node><parent a="34"><child>A text</child></parent></root_node>')

    def test_child_of_child_with_attrs_or_text_and_newlines(self):
        self.assert_xml_equals_dict({'parent': {'_attrs': {'a': '34'}, 'child': 'A text'}},
                                    '''<root_node>
                                        <parent a="34">
                                            <child>
                                                A text
                                            </child>
                                        </parent>
                                    </root_node>''')

    def test_that_element_with_text_and_attrs_is_supported(self):
        self.assert_xml_equals_dict({'parent': {'child': {'_attrs': {'an_attr': '42', 'public': 'true'}, 'text': 'The text'}}},
                                    '<root_node><parent><child an_attr="42" public="true">The text</child>'
                                    '</parent></root_node>')

    def test_child_have_same_childs_such_as_posts(self):
        self.assert_xml_equals_dict({'posts': {'post': ['A', 'B']}},
                                    '<root_node><posts><post>A</post><post>B</post></posts></root_node>')
