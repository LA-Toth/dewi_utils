import unittest.mock
from dewi.main import main
import dewi.tests


@unittest.mock.patch('dewi.main.myprint')
class MainTest(dewi.tests.TestCase):
    def test_main(self, print_mock: unittest.mock.Mock):
        main()
        print_mock.assert_called_once_with('DEWI is started')
