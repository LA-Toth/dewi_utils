# Copyright 2015-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import io
import sys

import dewi.tests

from dewi.tests import redirect_outputs


class TestRedirection(dewi.tests.TestCase):
    def test_can_capture_printing_during_test(self):
        with redirect_outputs() as output:
            print("Hello stdout!")
            print("Hello stderr!", file=sys.stderr)

        self.assert_equal("Hello stdout!\n", output.stdout.getvalue())
        self.assert_equal("Hello stderr!\n", output.stderr.getvalue())

    def test_is_reentrant_if_stdout_or_stderr_is_specified(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_outputs(stdout, stderr):
            print("Before inner stdout")
            print("Before inner stderr", file=sys.stderr)

            with redirect_outputs(stdout=stdout, stderr=stderr):
                print("Inner stdout")
                print("Inner stderr", file=sys.stderr)

            print("After inner stdout")
            print("After inner stderr", file=sys.stderr)

        self.assert_equal("Before inner stdout\nInner stdout\nAfter inner stdout\n", stdout.getvalue())
        self.assert_equal("Before inner stderr\nInner stderr\nAfter inner stderr\n", stderr.getvalue())

    def test_is_not_reentrant_without_args(self):
        with redirect_outputs() as outer:
            print("Before inner stdout")
            print("Before inner stderr", file=sys.stderr)

            with redirect_outputs() as inner:
                print("Inner stdout")
                print("Inner stderr", file=sys.stderr)

            print("After inner stdout")
            print("After inner stderr", file=sys.stderr)

        self.assert_equal("Before inner stdout\nAfter inner stdout\n", outer.stdout.getvalue())
        self.assert_equal("Before inner stderr\nAfter inner stderr\n", outer.stderr.getvalue())

        self.assert_equal("Inner stdout\n", inner.stdout.getvalue())
        self.assert_equal("Inner stderr\n", inner.stderr.getvalue())
