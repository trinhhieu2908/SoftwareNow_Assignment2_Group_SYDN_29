

import os
import tempfile
import unittest
from evaluator import tokenize, tokens_to_str, parse, node_to_str, eval_node, evaluate_file, fmt_result



# Tokeniser tests
 

class TestTokenize(unittest.TestCase):

    def _types(self, expr):
        return [t for t, _ in tokenize(expr)]

    def _values(self, expr):
        return [v for _, v in tokenize(expr)]

    def test_simple_addition(self):
        toks = tokenize("3 + 5")
        self.assertEqual(toks, [("NUM", "3"), ("OP", "+"), ("NUM", "5"), ("END", "END")])

    def test_unary_minus_separate_token(self):
        """Unary '-' must NOT be folded into the number token."""
        toks = tokenize("-5")
        self.assertIn(("OP", "-"), toks)
        self.assertIn(("NUM", "5"), toks)

    def test_parentheses(self):
        toks = tokenize("(3 + 4)")
        self.assertIn(("LPAREN", "("), toks)
        self.assertIn(("RPAREN", ")"), toks)

    def test_decimal_number(self):
        toks = tokenize("3.14")
        self.assertEqual(toks[0], ("NUM", "3.14"))

    def test_invalid_character_raises(self):
        with self.assertRaises(ValueError):
            tokenize("3 @ 5")

    def test_whitespace_ignored(self):
        toks1 = tokenize("3+5")
        toks2 = tokenize("3 + 5")
        self.assertEqual(toks1, toks2)

    def test_end_token_always_last(self):
        toks = tokenize("1 + 2")
        self.assertEqual(toks[-1], ("END", "END"))


# tokens_to_str tests

class TestTokensToStr(unittest.TestCase):

    def test_simple_format(self):
        toks = tokenize("3 + 5")
        self.assertEqual(tokens_to_str(toks), "[NUM:3] [OP:+] [NUM:5] [END]")

    def test_parentheses_format(self):
        toks = tokenize("(1)")
        result = tokens_to_str(toks)
        self.assertIn("[LPAREN:(]", result)
        self.assertIn("[RPAREN:)]", result)


# Parser + AST string tests

class TestParse(unittest.TestCase):

    def _tree(self, expr):
        return node_to_str(parse(tokenize(expr)))

    def test_simple_add(self):
        self.assertEqual(self._tree("3 + 5"), "(+ 3 5)")

    def test_precedence_mul_before_add(self):
        self.assertEqual(self._tree("2 + 3 * 4"), "(+ 2 (* 3 4))")

    def test_unary_negation(self):
        self.assertEqual(self._tree("-(3 + 4)"), "(neg (+ 3 4))")

    def test_double_negation(self):
        self.assertEqual(self._tree("--5"), "(neg (neg 5))")

    def test_complex_expression(self):
        self.assertEqual(
            self._tree("(10 - 2) * 3 + -4 / 2"),
            "(+ (* (- 10 2) 3) (/ (neg 4) 2))"
        )

    def test_implicit_multiplication(self):
        tree = self._tree("2(3 + 4)")
        self.assertIn("*", tree)

    def test_unary_plus_raises(self):
        with self.assertRaises(ValueError):
            parse(tokenize("+5"))

    def test_mismatched_paren_raises(self):
        with self.assertRaises(ValueError):
            parse(tokenize("(3 + 4"))

    def test_unexpected_rparen_raises(self):
        with self.assertRaises(ValueError):
            parse(tokenize("3 + 4)"))

    def test_nested_parens(self):
        tree = self._tree("((3 + 4))")
        self.assertEqual(tree, "(+ 3 4)")


# Evaluator tests


class TestEvalNode(unittest.TestCase):

    def _eval(self, expr):
        return eval_node(parse(tokenize(expr)))

    def test_addition(self):
        self.assertAlmostEqual(self._eval("3 + 5"), 8.0)

    def test_subtraction(self):
        self.assertAlmostEqual(self._eval("10 - 3"), 7.0)

    def test_multiplication(self):
        self.assertAlmostEqual(self._eval("4 * 5"), 20.0)

    def test_division(self):
        self.assertAlmostEqual(self._eval("10 / 4"), 2.5)

    def test_unary_negation(self):
        self.assertAlmostEqual(self._eval("-(3 + 4)"), -7.0)

    def test_double_negation(self):
        self.assertAlmostEqual(self._eval("--5"), 5.0)

    def test_operator_precedence(self):
        self.assertAlmostEqual(self._eval("2 + 3 * 4"), 14.0)

    def test_parentheses_override_precedence(self):
        self.assertAlmostEqual(self._eval("(2 + 3) * 4"), 20.0)

    def test_complex_expression(self):
        # (10-2)*3 + (-4)/2 = 24 + (-2) = 22
        self.assertAlmostEqual(self._eval("(10 - 2) * 3 + -4 / 2"), 22.0)

    def test_division_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            self._eval("1 / 0")

    def test_nested_parentheses(self):
        self.assertAlmostEqual(self._eval("((2 + 3) * (4 - 1))"), 15.0)

    def test_negative_result(self):
        self.assertAlmostEqual(self._eval("3 - 10"), -7.0)

    def test_implicit_multiplication(self):
        self.assertAlmostEqual(self._eval("2(3 + 4)"), 14.0)

# fmt_result tests

class TestFmtResult(unittest.TestCase):

    def test_whole_number_no_decimal(self):
        self.assertEqual(fmt_result(8.0), "8")

    def test_fraction_four_decimal_places(self):
        self.assertEqual(fmt_result(1 / 3), "0.3333")

    def test_negative_whole(self):
        self.assertEqual(fmt_result(-7.0), "-7")

    def test_negative_fraction(self):
        self.assertEqual(fmt_result(-1 / 3), "-0.3333")


# evaluate_file integration tests

class TestEvaluateFile(unittest.TestCase):

    def _run(self, lines):
        """Write *lines* to a temp file, run evaluate_file, return results."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                        delete=False, encoding="utf-8") as fh:
            fh.write("\n".join(lines))
            path = fh.name
        try:
            return evaluate_file(path)
        finally:
            os.unlink(path)
            out = os.path.join(os.path.dirname(path), "output.txt")
            if os.path.exists(out):
                os.unlink(out)

    def test_returns_list_of_dicts(self):
        results = self._run(["3 + 5"])
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)

    def test_dict_keys_present(self):
        result = self._run(["3 + 5"])[0]
        self.assertIn("input", result)
        self.assertIn("tree", result)
        self.assertIn("tokens", result)
        self.assertIn("result", result)

    def test_correct_result_value(self):
        result = self._run(["3 + 5"])[0]
        self.assertAlmostEqual(result["result"], 8.0)

    def test_invalid_char_returns_error(self):
        result = self._run(["3 @ 5"])[0]
        self.assertEqual(result["result"], "ERROR")
        self.assertEqual(result["tree"],   "ERROR")
        self.assertEqual(result["tokens"], "ERROR")

    def test_division_by_zero_returns_error(self):
        result = self._run(["1 / 0"])[0]
        self.assertEqual(result["result"], "ERROR")
        # tokens and tree should still be set
        self.assertNotEqual(result["tokens"], "ERROR")
        self.assertNotEqual(result["tree"],   "ERROR")

    def test_sample_input_matches_expected(self):
        """Full integration test against the provided sample_input.txt."""
        lines = [
            "3 + 5",
            "2 + 3 * 4",
            "-(3 + 4)",
            "--5",
            "(10 - 2) * 3 + -4 / 2",
            "3 @ 5",
            "1 / 0",
        ]
        expected_results = [8.0, 14.0, -7.0, 5.0, 22.0, "ERROR", "ERROR"]
        results = self._run(lines)

        for i, (r, exp) in enumerate(zip(results, expected_results)):
            if exp == "ERROR":
                self.assertEqual(r["result"], "ERROR", msg=f"Line {i}: {lines[i]}")
            else:
                self.assertAlmostEqual(r["result"], exp, msg=f"Line {i}: {lines[i]}")

    def test_output_file_written(self):
        """evaluate_file must write output.txt to the same directory as input."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                        delete=False, encoding="utf-8") as fh:
            fh.write("3 + 5\n")
            path = fh.name
        try:
            evaluate_file(path)
            out = os.path.join(os.path.dirname(path), "output.txt")
            self.assertTrue(os.path.exists(out))
        finally:
            os.unlink(path)
            if os.path.exists(out):
                os.unlink(out)

    def test_multiple_expressions(self):
        results = self._run(["1 + 1", "2 * 3", "10 / 5"])
        self.assertEqual(len(results), 3)
        self.assertAlmostEqual(results[0]["result"], 2.0)
        self.assertAlmostEqual(results[1]["result"], 6.0)
        self.assertAlmostEqual(results[2]["result"], 2.0)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
