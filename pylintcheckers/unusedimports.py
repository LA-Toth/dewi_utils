import ast

from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker

from logilab.common.testlib import unittest_main
from astroid import test_utils
from pylint.testutils import CheckerTestCase, Message


MSGS = {
    'W1611': (
        'Unused import %s',
        'nnx-unused-import',
        'Used when an imported module or variable is not used.'
    ),
}


class UnusedImportsChecker(BaseChecker):
    # The AST wrapper used by Pylint skips annotation nodes, thus, unable to
    # mark a name that appears in an annotation used. This leads to a lot of
    # false-positive unused-import warnings when an imported name is only used
    # in annotations. Since we cannot use IAstroidChecker due to the above
    # reason, this checker is implemented as a raw source code based checker,
    # using Python's built-in AST module, that is aware of annotations.
    __implements__ = IRawChecker

    name = 'dewi'
    msgs = MSGS

    options = ()

    def process_module(self, module):
        source = self._read_source(module)
        imported_names = set(module.wildcard_import_names())
        used_names = self.__collect_used_names(source)

        for name in imported_names.difference(used_names):
            self.add_message('W1611', args=(name,), line=0)

    def __collect_used_names(self, source):
        tree = ast.parse(source)
        used_names_collector = _UsedNamesCollector()
        used_names_collector.visit(tree)

        return used_names_collector.used_names

    def _read_source(self, module):
        return module.file_stream.read()


# Note: since this class collects all used names naively, without taking scoping
#       rules into consideration, it is possible in some corner cases for some
#       unused imports to skip through the checker. For day-to-day code,
#       however, this implementation is good enough.
class _UsedNamesCollector(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.used_names = set()

    def __note_used_name(self, name):
        self.used_names.add(name)

    def visit_Name(self, node):
        self.__note_used_name(node.id)

    def visit_FunctionDef(self, node):
        self.__note_used_name(node.name)
        super().generic_visit(node)

    def visit_ClassDef(self, node):
        self.__note_used_name(node.name)
        super().generic_visit(node)


class _TestableUnusedImportsChecker(UnusedImportsChecker):
    def __init__(self, linter):
        super().__init__(linter)
        self.source_code_str = ""

    def _read_source(self, module):
        return self.source_code_str


TEST_SOURCE_CODE = """\
from somemodule import UsedInFunctionAnnotation, ImportedClass as UsedInFunctionBody
from somemodule import UsedInMethodAnnotation, OtherImportedClass as UsedInMethodBody
from somemodule import used_decorator
from somemodule import UnusedImportedName

import usedinfunc, usedinmethod
import unusedimportedmodule


some_variable = 42


def some_function(arg: UsedInFunctionAnnotation) -> usedinfunc.TheReturnType:
    return UsedInFunctionBody()


class SomeClass:
    @used_decorator
    def some_method(self, arg: (None, UsedInMethodAnnotation)) -> usedinmethod.TheReturnType:
        return UsedInMethodBody()
"""


class TestUnusedImportsChecker(CheckerTestCase):
    CHECKER_CLASS = _TestableUnusedImportsChecker

    def test_unused_imports_in_normal_source_file(self):
        self.checker.source_code_str = TEST_SOURCE_CODE

        module = test_utils.build_module(TEST_SOURCE_CODE)
        module.file = "unusedimporttestexample.py"

        expected_message_1 = Message(msg_id='W1611', args=('UnusedImportedName',), line=0)
        expected_message_2 = Message(msg_id='W1611', args=('unusedimportedmodule',), line=0)

        with self.assertAddsMessages(expected_message_1, expected_message_2):
            self.checker.process_module(module)


def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(UnusedImportsChecker(linter))


if __name__ == '__main__':
    unittest_main()
