import unittest
import unittest.mock
from dewi.main import main


@unittest.mock.patch('dewi.main.myprint')
class MainTest(unittest.TestCase):
    def test_main(self, print_mock: unittest.mock.Mock):
        main()
        print_mock.assert_called_once_with('DEWI is started')
