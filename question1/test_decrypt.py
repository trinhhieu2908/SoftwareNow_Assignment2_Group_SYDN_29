import unittest
from encrypt import encrypt
from decrypt import decrypt


class TestDecrypt(unittest.TestCase):

    def test_lowercase(self):
        text = "hello"
        s1, s2 = 2, 3
        encrypted = encrypt(text, s1, s2)
        self.assertEqual(decrypt(encrypted, s1, s2), text)

    def test_uppercase(self):
        text = "HELLO"
        s1, s2 = 2, 3
        encrypted = encrypt(text, s1, s2)
        self.assertEqual(decrypt(encrypted, s1, s2), text)

    def test_mixed(self):
        text = "Hello World!"
        s1, s2 = 2, 3
        encrypted = encrypt(text, s1, s2)
        self.assertEqual(decrypt(encrypted, s1, s2), text)

    def test_edge_letters(self):
        text = "a m n z A M N Z"
        s1, s2 = 2, 3
        encrypted = encrypt(text, s1, s2)
        self.assertEqual(decrypt(encrypted, s1, s2), text)

    def test_zero_shift(self):
        text = "Test123!"
        s1, s2 = 0, 0
        encrypted = encrypt(text, s1, s2)
        self.assertEqual(decrypt(encrypted, s1, s2), text)


if __name__ == "__main__":
    unittest.main()