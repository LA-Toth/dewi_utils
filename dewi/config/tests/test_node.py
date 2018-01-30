# Copyright 2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3
import typing

import yaml

import dewi.tests
from dewi.config.node import Node, NodeList


class N1(Node):
    def __init__(self):
        self.x: int = 0
        self.y: int = None


class N2(Node):
    def __init__(self):
        self.members: typing.List[N1] = NodeList(N1)
        self.title: str = None
        self.count: int = 100


NODE_TEST_RESULT = """count: 100
members:
- {x: 0, y: null}
- {x: 0, y: 42}
title: null
"""

NODE_EMPTY_RESULT = """count: 100
members: []
title: null
"""


class NodeAndNodeListTest(dewi.tests.TestCase):
    def set_up(self):
        self.tested = N2()
        self.tested.members.append(N1())

        z = N1()
        z.y = 42
        self.tested.members.append(z)

    def test_empty_object(self):
        self.assert_equal(NODE_EMPTY_RESULT, yaml.dump(N2()))
        self.tested = N2()
        self.assert_equal(NODE_EMPTY_RESULT, yaml.dump(self.tested))

    def test_yaml_dump(self):
        self.assert_equal(NODE_TEST_RESULT, yaml.dump(self.tested))

    def test_load_from_dict(self):
        self.tested = N2()
        self.assert_equal(NODE_EMPTY_RESULT, yaml.dump(self.tested))
        self.tested.load_from(dict(members=[dict(x=0, y=None), dict(x=0, y=42)], title=None))
        self.assert_equal(NODE_TEST_RESULT, yaml.dump(self.tested))

    def test_load_from_yaml(self):
        self.tested = N2()
        self.assert_equal(NODE_EMPTY_RESULT, yaml.dump(self.tested))
        self.tested.load_from(yaml.load(NODE_TEST_RESULT))
        self.assert_equal(NODE_TEST_RESULT, yaml.dump(self.tested))

    def test_size_of_empty_object(self):
        self.assert_equal(3, len(N2()))

    def test_size_of_filled_object(self):
        self.assert_equal(3, len(self.tested))

    def test_size_of_node_list_equals_item_count(self):
        self.assert_equal(2, len(self.tested.members))
