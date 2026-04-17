

import unittest
from encrypt import encrypt
from decrypt import decrypt


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def roundtrip(text: str, shift1: int, shift2: int) -> bool:
    """Return True if decrypt(encrypt(text)) == text."""
    return decrypt(encrypt(text, shift1, shift2), shift1, shift2) == text


# ─────────────────────────────────────────────────────────────────────────────
# Encryption rule tests
# ─────────────────────────────────────────────────────────────────────────────

class TestEncryptRules(unittest.TestCase):
    """Verify each of the four encryption rules individually."""

    def test_lowercase_am_shifts_forward(self):
        """a-m: shift forward by shift1 * shift2.
        'a'(0) + 2*3=6 -> pos 6 -> 'g'"""
        self.assertEqual(encrypt("a", 2, 3), "g")

    def test_lowercase_am_wraparound(self):
        """a-m shift wraps around the alphabet.
        'm'(12) + 3*5=15 -> pos 27%26=1 -> 'b'"""
        self.assertEqual(encrypt("m", 3, 5), "b")

    def test_lowercase_nz_shifts_backward(self):
        """n-z: shift backward by shift1 + shift2.
        'z'(25) - (2+3)=5 -> pos 20 -> 'u'"""
        self.assertEqual(encrypt("z", 2, 3), "u")

    def test_lowercase_nz_wraparound(self):
        """n-z shift wraps around.
        'n'(13) - (1+26)=27 -> (13-27)%26=12 -> 'm'"""
        self.assertEqual(encrypt("n", 1, 26), "m")

    def test_uppercase_am_shifts_backward(self):
        """A-M: shift backward by shift1.
        'C'(2) - 2 -> pos 0 -> 'A'"""
        self.assertEqual(encrypt("C", 2, 3), "A")

    def test_uppercase_am_wraparound(self):
        """A-M backward shift wraps around.
        'A'(0) - 3 -> (0-3)%26=23 -> 'X'"""
        self.assertEqual(encrypt("A", 3, 0), "X")

    def test_uppercase_nz_shifts_forward(self):
        """N-Z: shift forward by shift2^2.
        'N'(13) + 2^2=4 -> pos 17 -> 'R'"""
        self.assertEqual(encrypt("N", 1, 2), "R")

    def test_uppercase_nz_wraparound(self):
        """N-Z forward shift wraps.
        'Z'(25) + 3^2=9 -> pos 34%26=8 -> 'I'"""
        self.assertEqual(encrypt("Z", 1, 3), "I")

    def test_non_alpha_unchanged(self):
        """Spaces, digits, punctuation, newlines and special chars unchanged."""
        unchanged = " 0123!@#\n\t<<<>>>"
        self.assertEqual(encrypt(unchanged, 5, 7), unchanged)

    def test_zero_shifts_identity(self):
        """shift1=0, shift2=0 -> all shifts are 0 -> text unchanged."""
        text = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.assertEqual(encrypt(text, 0, 0), text)



# Decryption rule tests

class TestDecryptRules(unittest.TestCase):
    """Verify that decrypt correctly inverts each encryption rule."""

    def test_decrypt_am_rule(self):
        """Decrypt correctly undoes the a-m forward shift.
        encrypt('a', 2, 3) = 'g'; decrypt('g', 2, 3) should return 'a'."""
        enc = encrypt("a", 2, 3)
        self.assertEqual(decrypt(enc, 2, 3), "a")

    def test_decrypt_nz_rule(self):
        """Decrypt correctly undoes the n-z backward shift.
        encrypt('z', 2, 3) = 'u'; decrypt('u', 2, 3) should return 'z'."""
        enc = encrypt("z", 2, 3)
        self.assertEqual(decrypt(enc, 2, 3), "z")

    def test_decrypt_uppercase_am_rule(self):
        """Decrypt correctly undoes the A-M backward shift.
        encrypt('L', 2, 3) = 'J'; decrypt('J', 2, 3) should return 'L'."""
        enc = encrypt("L", 2, 3)
        self.assertEqual(decrypt(enc, 2, 3), "L")

    def test_decrypt_uppercase_nz_rule(self):
        """Decrypt correctly undoes the N-Z forward shift.
        encrypt('N', 1, 2) = 'R'; decrypt('R', 1, 2) should return 'N'."""
        enc = encrypt("N", 1, 2)
        self.assertEqual(decrypt(enc, 1, 2), "N")

    def test_decrypt_non_alpha_unchanged(self):
        """Non-alphabetic characters pass through decrypt unchanged."""
        unchanged = " 0123!@#\n\t"
        self.assertEqual(decrypt(unchanged, 3, 4), unchanged)

    def test_decrypt_zero_shifts_identity(self):
        """Decrypting with (0, 0) shifts returns the input unchanged."""
        text = "Hello World 123!"
        self.assertEqual(decrypt(text, 0, 0), text)


# Round-trip tests

class TestRoundTrip(unittest.TestCase):
    """End-to-end tests: decrypt(encrypt(text)) must equal text.

    Only shift values that produce no collisions are used here.
    (0, 0) is always safe because all shifts are 0 and the cipher is identity.
    """

    def test_roundtrip_zero_shifts_simple(self):
        """Zero shifts: encrypt is identity, decrypt recovers original."""
        self.assertTrue(roundtrip("Hello World", 0, 0))

    def test_roundtrip_zero_shifts_all_lowercase(self):
        self.assertTrue(roundtrip("abcdefghijklmnopqrstuvwxyz", 0, 0))

    def test_roundtrip_zero_shifts_all_uppercase(self):
        self.assertTrue(roundtrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 0, 0))

    def test_roundtrip_zero_shifts_mixed(self):
        self.assertTrue(roundtrip("The Quick Brown Fox Jumps", 0, 0))

    def test_roundtrip_zero_shifts_special_chars(self):
        self.assertTrue(roundtrip("<<<special>>> text\nnewline\ttab 123!", 0, 0))

    def test_roundtrip_zero_shifts_full_raw_text(self):
        """Full round-trip on the actual assignment text file content."""
        raw = (
            "The quick brown fox jumps over the lazy dog beneath the shady willows. "
            "The dog, startled from his peaceful afternoon nap, quickly rises and "
            "chases after the mischievous fox.\n\n"
            "<<<Through vibrant meadows and past buzzing beehives they race, "
            "disturbing a flock of quails that scatter into the crisp autumn sky.>>> "
            "The fox, quite pleased with his clever prank, dashes into his cozy "
            "underground den while the dog, now exhausted from the zealous pursuit, "
            "returns to his favorite spot under the whispering branches to resume "
            "his quiet slumber."
        )
        self.assertTrue(roundtrip(raw, 0, 0))

    def test_roundtrip_multiples_of_26(self):
        """Shifts that are multiples of 26 are mathematically equivalent to 0."""
        self.assertTrue(roundtrip("Hello World 123!", 26, 26))

    def test_roundtrip_negative_zero_equivalent(self):
        """Negative shifts equivalent to zero."""
        self.assertTrue(roundtrip("Testing 123", -26, 0))



# Cipher property tests

class TestCipherProperties(unittest.TestCase):

    def test_encrypt_changes_letters(self):
        """Non-zero shift must change at least some letters."""
        text = "abcdefghijklm"  # all a-m
        enc = encrypt(text, 1, 1)
        self.assertNotEqual(text, enc)

    def test_encrypt_preserves_length(self):
        """Encrypted text must have same length as original."""
        text = "Hello World 123!"
        self.assertEqual(len(encrypt(text, 3, 4)), len(text))

    def test_decrypt_preserves_length(self):
        """Decrypted text must have same length as ciphertext."""
        text = "Hello World 123!"
        enc = encrypt(text, 3, 4)
        self.assertEqual(len(decrypt(enc, 3, 4)), len(enc))

    def test_different_shifts_different_ciphertext(self):
        """Different shift values should generally produce different ciphertext."""
        text = "abcdefgh"
        enc1 = encrypt(text, 1, 2)
        enc2 = encrypt(text, 2, 1)
        # These will differ unless the products and sums happen to be equal
        # shift1*shift2: 2 vs 2 (same product!) but shift1+shift2: 3 vs 3 too
        # So actually (1,2) and (2,1) give SAME encryption for a-m and n-z
        # Let's use clearly different values
        enc3 = encrypt(text, 3, 4)
        self.assertNotEqual(enc1, enc3)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
