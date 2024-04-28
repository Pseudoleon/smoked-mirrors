import os
import sys
from io import StringIO
from contextlib import redirect_stdout
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
import traceback

INTERPRETER_NAME = "<funny sand>"

class InterpreterError(Exception): pass

def last_stack_from(trace):
    trace = traceback.extract_tb(trace)
    i = len(trace) - 1
    while i >= 0:
        if trace[i].filename == INTERPRETER_NAME:
            return trace[i]
        i -= 1
    return trace[0]

# Performs exec and checks for errors
# returns None if there are no errors
# returns (error class, line in snippet, error message) if there are errors
def check_exec(cmd):
    global_vars = {}
    # "bubble_sort is not defined" if local_vars is supplied

    try:
        exec(cmd, global_vars)
    except SyntaxError as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        line_number = err.lineno
    except Exception as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        last_interp_frame = last_stack_from(tb)
        line_number = last_interp_frame[1]
    else:
        return None
    return (error_class, line_number, detail)


# Returns (bytecode, has_error, (error class, line in snippet, error message))
def try_compile_restricted(code):
    bytecode = None
    try:
        # bytecode = compile_restricted(code, '<inline>', 'exec')
        bytecode = compile(code, INTERPRETER_NAME, 'exec')
    except SyntaxError as err:
        error_class = err.__class__.__name__
        line_number = err.lineno
        detail = err.args[0]
    except Exception as err:
        error_class = err.__class__.__name__
        cl, exc, tb = sys.exc_info()
        last_interp_frame = last_stack_from(tb)
        line_number = last_interp_frame[1]
        detail = err.args[0]
    else:
        return (bytecode, False, None)
    return (None, True, (error_class, line_number, detail))

# Takes in code, returns (line, error class, error message)
# returns None if there is no error
def get_error(code):
    if code.strip().count("\n") <= 1:
        print(f"WARN: Code detected as single line: {code}")
        return None

    if "input(" in code.strip():
        print(f"WARN: input() detected, skipping.." )
        return None

    safe_bytecode, has_error, compile_err = try_compile_restricted(code)
    if has_error:
        return compile_err

    # need to redirect stdout
    sout = StringIO()
    err = None

    with redirect_stdout(sout):
        err = check_exec(safe_bytecode)
    
    # print("stdout: ", sout.getvalue())
    if err != None and err[0] in ["ImportError", "ModuleNotFoundError"]:
        print("IMPORT ERROR. Consider importing. err: ", err)
        err = None
    return err

def test_get_error():
    code_examples = [
"""
print("awaw)
print("listen for meows!")
print("listen for woofs!")
""",
"""
def bubble_sort(arr):
    n = len(arr)
    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
def main():
    arr = [3, 2, 1, 4, 5, 6]
    print("Before sorting:", arr)
    bubble_sort(arr)
    print("After sorting:", arr)
main()
""",
"""
def divbz():
    x = 100 - 100
    return 10/x
divbz()
""",
"""
class Account:
    def __init__(self, balance):
        self.balance = balance
    def deposit(self, amount):
        self.balance += amount
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount
    def get_balance(self):
        return self.balance
class Bank:
    def __init__(self):
        self.accounts = {}
    def open_account(self, account_name, balance):
        self.accounts[account_name] = Account(balance)
    def deposit_to_account(self, account_name, amount):
        self.accounts[account_name].deposit(amount)
    def withdraw_from_account(self, account_name, amount):
        self.accounts[account_name].withdraw(amount)
    def get_account_balance(self, account_name):
        return self.accounts[account_name].get_balance()
bank = Bank()
bank.open_account("John Doe", 1000)
bank.deposit_to_account("John Doe", 500)
bank.withdraw_from_account("John Doe", 300)
print(bank.get_account_balance("John Doe"))
""",
"""
import numpy as np
import matplotlib.pyplot as plt
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)
def plot_fibonacci(n):
    x = np.linspace(0, n, n)
    plt.plot(x, fibonacci(n))
    plt.xlabel('Number')
    plt.ylabel('Fibonacci sequence')
    plt.show()
plot_fibonacci(10)
"""
    ]

    expected_outputs = [
        ('SyntaxError', 2, 'unterminated string literal (detected at line 2)'),
        None,
        ('ZeroDivisionError', 4, 'division by zero'),
        None,
        ('ValueError', 11, 'x and y must have same first dimension, but have shapes (10,) and (1,)'),

    ]

    if len(expected_outputs) != len(code_examples):
        print("FATAL: len(expected_outputs) != len(code_examples)")
        exit(1)

    for (inp, output) in zip(code_examples, expected_outputs):
        err = get_error(inp)
        if err != output:
            print(f"TEST FAILED (index {code_examples.index(inp)})\nGOT: {err}\nEXPECTED: {output}")
            exit(1)


if __name__ == "__main__":
    test_get_error()