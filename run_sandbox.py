import subprocess
import sys

def get_error(code):
    if code.strip().count("\n") <= 1:
        print(f"WARN: Code detected as single line: {code}")
        return None

    unsafe_code = ["input(", "os.system(", "open("]
    for unsf in unsafe_code:
        if unsf in code.strip():
            print(f"WARN: -> {unsf} <-  detected, skipping.." )
            return None

    proc = subprocess.Popen(
        ["./env/bin/python", "sandboxed.py", code],
        stdout=subprocess.PIPE
    )

    out_lines = proc.stdout.readlines()
    proc.kill()
    
    err = None

    if out_lines[0].strip().decode() != "None":
        err = (out_lines[0].strip().decode(), int(out_lines[1].strip().decode()), out_lines[2].strip().decode())

    if err != None and err[0] in ["ImportError", "ModuleNotFoundError"]:
        print("IMPORT ERROR. Consider importing. err: ", err)
        err = None
    
    # print(out_lines)
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
""",
"""
import os
os.system("/bin/sh")
print("OKAY")
"""
    ]

    expected_outputs = [
        ('SyntaxError', 2, 'unterminated string literal (detected at line 2)'),
        None,
        ('ZeroDivisionError', 4, 'division by zero'),
        None,
        ('ValueError', 11, 'x and y must have same first dimension, but have shapes (10,) and (1,)'),
        None
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