import os
import sys
from io import StringIO
from contextlib import redirect_stderr
from contextlib import redirect_stdout

import traceback

class InterpreterError(Exception): pass

# Performs exec and checks for errors
# returns None if there are no errors
# returns (error class, line in snippet, error message) if there are errors
def check_exec(cmd, globals=None, locals=None):
    try:
        exec(cmd, globals, locals)
    except SyntaxError as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        line_number = err.lineno
    except Exception as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        line_number = traceback.extract_tb(tb)[-1][1]
    else:
        return None
    return (error_class, line_number, detail) 

# Takes in code, returns (line, error class, error message)
# returns None if there is no error
def get_error(code):
    # need to redirect stdout
    sout = StringIO()
    err = None

    with redirect_stdout(sout):
        err = check_exec(code)
    
    # sout = sout.getvalue()
    return err

def test_get_error():
    code = """
def testing():
    aw = 8 / 0
print("all okay?")
testing()
    """
    
    get_error(code)


if __name__ == "__main__":
    test_get_error()