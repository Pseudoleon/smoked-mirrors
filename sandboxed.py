
import os
import sys
from io import StringIO
from contextlib import redirect_stdout
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
import traceback
import pyseccomp as seccomp

def drop_perms():
    filter = seccomp.SyscallFilter(seccomp.ERRNO(seccomp.errno.EPERM))
    filter.add_rule(
        seccomp.ALLOW, "write", seccomp.Arg(0, seccomp.EQ, sys.stdout.fileno())
    )
    filter.add_rule(
        seccomp.ALLOW, "write", seccomp.Arg(0, seccomp.EQ, sys.stderr.fileno())
    )
    filter.load()

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

if __name__ == "__main__":
    ret = get_error(sys.argv[1])
    if ret == None:
        print("None")
    else:
        for x in ret:
            print(x)
    