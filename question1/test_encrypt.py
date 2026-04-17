import unittest
from encrypt import encrypt


class TestEncrypt(unittest.TestCase):

    def test_lowercase_am(self):
        self.assertEqual(encrypt("a", 2, 3), "g")

    def test_lowercase_nz(self):
        self.assertEqual(encrypt("n", 2, 3), "v")

    def test_uppercase_AM(self):
        self.assertEqual(encrypt("A", 2, 3), "L")

    def test_uppercase_NZ(self):
        self.assertEqual(encrypt("N", 2, 3), "W")

    def test_mixed(self):
        self.assertEqual(encrypt("aN!", 2, 3), "gW!")


if __name__ == "__main__":
    unittest.main()