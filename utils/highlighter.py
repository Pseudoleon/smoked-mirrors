from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def format(code: str = None):
    hf = HtmlFormatter(style="solarized-dark", full=False, linenos="table", linespans="codeblockline")
    example = """
    import time
    start = time.time()
    def process():
        x = 12
        for _ in range(100):
            x = x ^ _
        return x

    process()
    delta = time.time() - start
    print(f"Time taken: {delta}")"""
    code = code or example
    pl = PythonLexer()
    #with open("index.html", "w") as ind:
    hl = highlight(code, pl, hf)

    return hl