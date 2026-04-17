"""
HIT137 Assignment 2 – Question 2
Mathematical Expression Evaluator  (evaluator.py)

Implements a recursive-descent parser with no classes.

Grammar (precedence low → high)
────────────────────────────────
  expr    →  term  ( ('+' | '-')  term  )*
  term    →  unary ( ('*' | '/')  unary | <implicit *> )*
  unary   →  '-' unary  |  primary
  primary →  NUMBER  |  '(' expr ')'

Implicit multiplication is handled at the *term* level: two consecutive
primaries (a number or a parenthesised group) are treated as multiplication.

Public API
──────────
  evaluate_file(input_path: str) -> list[dict]
      Reads expressions one-per-line from *input_path*, writes output.txt
      to the same directory, and returns a list of result dicts.
"""

import os


# ═══════════════════════════════════════════════════════════════════════════════
# Tokeniser
# ═══════════════════════════════════════════════════════════════════════════════

def tokenize(expr):
    """
    Convert *expr* into a list of (type, value) tuples.
    Raises ValueError for any unrecognised character.

    Token types: NUM, OP, LPAREN, RPAREN, END
    """
    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit() or ch == '.':          # numeric literal
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(('NUM', expr[i:j]))
            i = j

        elif ch in '+-*/':
            tokens.append(('OP', ch))
            i += 1

        elif ch == '(':
            tokens.append(('LPAREN', '('))
            i += 1

        elif ch == ')':
            tokens.append(('RPAREN', ')'))
            i += 1

        else:
            raise ValueError(f"Invalid character '{ch}' in expression")

    tokens.append(('END', 'END'))
    return tokens


def tokens_to_str(tokens):
    """
    Format a token list as the required '[TYPE:value] … [END]' string.
    e.g. [NUM:3] [OP:+] [NUM:5] [END]
    """
    parts = []
    for typ, val in tokens:
        if   typ == 'END':    parts.append('[END]')
        elif typ == 'NUM':    parts.append(f'[NUM:{val}]')
        elif typ == 'OP':     parts.append(f'[OP:{val}]')
        elif typ == 'LPAREN': parts.append('[LPAREN:(]')
        elif typ == 'RPAREN': parts.append('[RPAREN:)]')
    return ' '.join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# Recursive-descent parser
# Returns a nested-tuple AST:
#   ('num',   float_value)
#   ('neg',   operand_node)
#   ('binop', op_str, left_node, right_node)
# ═══════════════════════════════════════════════════════════════════════════════

def parse(tokens):
    """Parse *tokens* into an AST.  Raises ValueError on syntax errors."""
    pos = [0]   # mutable box so inner functions can advance the index

    def peek():
        return tokens[pos[0]]

    def consume():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    # ── expr: lowest precedence – addition and subtraction ───────────────────
    def parse_expr():
        left = parse_term()
        while peek()[0] == 'OP' and peek()[1] in ('+', '-'):
            op    = consume()[1]
            right = parse_term()
            left  = ('binop', op, left, right)
        return left

    # ── term: explicit * / and implicit multiplication ───────────────────────
    def parse_term():
        left = parse_unary()
        while True:
            if peek()[0] == 'OP' and peek()[1] in ('*', '/'):
                op    = consume()[1]
                right = parse_unary()
                left  = ('binop', op, left, right)
            elif peek()[0] in ('NUM', 'LPAREN'):
                # Implicit multiplication: two adjacent primaries
                right = parse_unary()
                left  = ('binop', '*', left, right)
            else:
                break
        return left

    # ── unary: negation or hand-off to primary ───────────────────────────────
    def parse_unary():
        if peek()[0] == 'OP' and peek()[1] == '-':
            consume()
            operand = parse_unary()        # right-associative
            return ('neg', operand)
        if peek()[0] == 'OP' and peek()[1] == '+':
            raise ValueError("Unary '+' is not supported")
        return parse_primary()

    # ── primary: number literal or parenthesised sub-expression ─────────────
    def parse_primary():
        tok = peek()
        if tok[0] == 'NUM':
            consume()
            return ('num', float(tok[1]))
        if tok[0] == 'LPAREN':
            consume()
            node = parse_expr()
            if peek()[0] != 'RPAREN':
                raise ValueError("Expected closing ')'")
            consume()
            return node
        if tok[0] == 'RPAREN':
            raise ValueError("Unexpected ')'")
        if tok[0] == 'END':
            raise ValueError("Unexpected end of input")
        raise ValueError(f"Unexpected token: {tok}")

    tree = parse_expr()
    if peek()[0] != 'END':
        raise ValueError(f"Unexpected token after expression: {peek()}")
    return tree


# ═══════════════════════════════════════════════════════════════════════════════
# AST → display string
# ═══════════════════════════════════════════════════════════════════════════════

def node_to_str(node):
    """
    Serialise an AST node to the required prefix notation, e.g.
      (+ 3 5)   (neg (+ 3 4))   (* 2 (- 10 5))
    """
    kind = node[0]
    if kind == 'num':
        v = node[1]
        return str(int(v)) if v == int(v) else str(v)
    if kind == 'neg':
        return f'(neg {node_to_str(node[1])})'
    if kind == 'binop':
        _, op, left, right = node
        return f'({op} {node_to_str(left)} {node_to_str(right)})'
    raise ValueError(f"Unknown AST node kind: {kind!r}")


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluator
# ═══════════════════════════════════════════════════════════════════════════════

def eval_node(node):
    """Recursively evaluate an AST node.  Raises ZeroDivisionError as needed."""
    kind = node[0]
    if kind == 'num':
        return node[1]
    if kind == 'neg':
        return -eval_node(node[1])
    if kind == 'binop':
        _, op, left, right = node
        lv = eval_node(left)
        rv = eval_node(right)
        if op == '+': return lv + rv
        if op == '-': return lv - rv
        if op == '*': return lv * rv
        if op == '/':
            if rv == 0:
                raise ZeroDivisionError("Division by zero")
            return lv / rv
    raise ValueError(f"Unknown AST node kind: {kind!r}")


# ═══════════════════════════════════════════════════════════════════════════════
# Formatting helpers
# ═══════════════════════════════════════════════════════════════════════════════

def fmt_result(v):
    """
    Format a numeric result:
      - whole numbers  →  no decimal point  (8.0 → '8')
      - fractions      →  rounded to 4 d.p. (1.33333 → '1.3333')
    """
    if v == int(v):
        return str(int(v))
    return f'{v:.4f}'


# ═══════════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════════

def evaluate_file(input_path: str) -> list:
    """
    Read expressions (one per line) from *input_path*.
    Write 'output.txt' to the same directory.
    Return a list of dicts, one per expression:
        {
            'input':   str,           # original expression
            'tree':    str,           # prefix-notation tree, or 'ERROR'
            'tokens':  str,           # token string, or 'ERROR'
            'result':  float | 'ERROR'
        }
    """
    out_dir  = os.path.dirname(os.path.abspath(input_path))
    out_path = os.path.join(out_dir, 'output.txt')

    with open(input_path, 'r', encoding='utf-8') as fh:
        lines = [ln.rstrip('\n') for ln in fh]

    results       = []
    output_blocks = []

    for expr in lines:
        entry = {
            'input':  expr,
            'tree':   'ERROR',
            'tokens': 'ERROR',
            'result': 'ERROR',
        }

        try:
            toks           = tokenize(expr)
            entry['tokens'] = tokens_to_str(toks)

            tree           = parse(toks)
            entry['tree']  = node_to_str(tree)

            val            = eval_node(tree)
            entry['result'] = val          # float on success

        except ZeroDivisionError:
            pass   # tokens + tree were already set; result stays 'ERROR'

        except Exception:
            pass   # tokens/tree may still be 'ERROR' – that is intentional

        results.append(entry)

        # Build the four-line output block
        r = entry['result']
        result_str = fmt_result(r) if r != 'ERROR' else 'ERROR'
        output_blocks.append(
            f"Input: {expr}\n"
            f"Tree: {entry['tree']}\n"
            f"Tokens: {entry['tokens']}\n"
            f"Result: {result_str}"
        )

    # Blocks separated by a blank line, with a final newline
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write('\n\n'.join(output_blocks) + '\n')

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# CLI entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage: python evaluator.py <input_file>')
        sys.exit(1)

    rs = evaluate_file(sys.argv[1])
    for r in rs:
        v = r['result']
        print(f"Input:   {r['input']}")
        print(f"Tree:    {r['tree']}")
        print(f"Tokens:  {r['tokens']}")
        print(f"Result:  {fmt_result(v) if v != 'ERROR' else 'ERROR'}")
        print()
