# HIT137 Assignment 2 - Question 2
# Mathematical Expression Evaluator
# Reads expressions from a file, parses and evaluates each one
# Uses recursive descent parsing with plain functions (no classes)
#
# How the parser works (from lowest to highest priority):
#   expr    -> handles + and -
#   term    -> handles * and / and implicit multiplication
#   unary   -> handles negative sign like -5 or -(3+4)
#   primary -> handles numbers and brackets

import os


# --- Tokeniser ---
# Breaks the raw expression string into a list of tokens
# Each token is a tuple like ('NUM', '3') or ('OP', '+')

def tokenize(expr):
   # go through each character and figure out what token it belongs to
    # raises ValueError if we find something we don't recognise (like @)
    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit() or ch == '.':         
                        # keep reading while we still have digits or decimal point
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
    # always add an END token so the parser knows when to stop
    tokens.append(('END', 'END'))
    return tokens


def tokens_to_str(tokens):
    # formats the token list into the required output string
    # e.g. [NUM:3] [OP:+] [NUM:5] [END]
    parts = []
    for typ, val in tokens:
        if   typ == 'END':    parts.append('[END]')
        elif typ == 'NUM':    parts.append(f'[NUM:{val}]')
        elif typ == 'OP':     parts.append(f'[OP:{val}]')
        elif typ == 'LPAREN': parts.append('[LPAREN:(]')
        elif typ == 'RPAREN': parts.append('[RPAREN:)]')
    return ' '.join(parts)


# --- Parser ---
# Takes the token list and builds an AST (abstract syntax tree)
# The tree is made of nested tuples:
#   ('num', value)               -> a number
#   ('neg', operand)             -> unary negation like -5
#   ('binop', op, left, right)   -> binary operation like 3 + 5

def parse(tokens):
    # we use a list with one element so the inner functions can update the position
    pos = [0]   

    def peek():
        return tokens[pos[0]]

    def consume():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

   
    def parse_expr():
        # handles + and - (lowest precedence)
        left = parse_term()
        while peek()[0] == 'OP' and peek()[1] in ('+', '-'):
            op    = consume()[1]
            right = parse_term()
            left  = ('binop', op, left, right)
        return left

    def parse_term():
         # handles * and / and also implicit multiplication like 2(3+4)
        left = parse_unary()
        while True:
            if peek()[0] == 'OP' and peek()[1] in ('*', '/'):
                op    = consume()[1]
                right = parse_unary()
                left  = ('binop', op, left, right)
            elif peek()[0] in ('NUM', 'LPAREN'):
                # two things next to each other means implicit multiplication
                right = parse_unary()
                left  = ('binop', '*', left, right)
            else:
                break
        return left

    def parse_unary():
                # handles the negative sign in front of a number or expression
        if peek()[0] == 'OP' and peek()[1] == '-':
            consume()
            operand = parse_unary()       
            return ('neg', operand)
        # unary + is not allowed per the assignment spec
        if peek()[0] == 'OP' and peek()[1] == '+':
            raise ValueError("Unary '+' is not supported")
        return parse_primary()

    def parse_primary():
                # handles a single number or a bracketed expression
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
        # if there are still tokens left after parsing, something is wrong
    if peek()[0] != 'END':
        raise ValueError(f"Unexpected token after expression: {peek()}")
    return tree

# --- Tree to string ---
# Converts the AST back into the required prefix notation string
# e.g. (+ 3 5)  or  (neg (+ 3 4))

def node_to_str(node):
   
    kind = node[0]
    if kind == 'num':
        v = node[1]
                # show whole numbers without decimal point e.g. 3 not 3.0
        return str(int(v)) if v == int(v) else str(v)
    if kind == 'neg':
        return f'(neg {node_to_str(node[1])})'
    if kind == 'binop':
        _, op, left, right = node
        return f'({op} {node_to_str(left)} {node_to_str(right)})'
    raise ValueError(f"Unknown AST node kind: {kind!r}")


# --- Evaluator ---
# Walks the AST and calculates the final numeric result

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


def fmt_result(v):
       # whole numbers show without decimal, fractions rounded to 4 places

    if v == int(v):
        return str(int(v))
    return f'{v:.4f}'


# --- Main function ---
# Reads the input file, processes each expression, writes output.txt

def evaluate_file(input_path: str) -> list:
        # output.txt goes in the same folder as the input file

    out_dir  = os.path.dirname(os.path.abspath(input_path))
    out_path = os.path.join(out_dir, 'output.txt')

    with open(input_path, 'r', encoding='utf-8') as fh:
        lines = [ln.rstrip('\n') for ln in fh]

    results       = []
    output_blocks = []

    for expr in lines:
                # default everything to ERROR, then update as each step succeeds
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
                        # tree and tokens are fine, only the result fails
            pass 

        except Exception:
                        # something went wrong earlier so tokens/tree stay as ERROR
            pass  
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

# run from command line: python evaluator.py <input_file>
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
