#!/usr/bin/env python3
"""Find names that are used before they are defined in a notebook.

Code cells are concatenated in order and checked with pyflakes, so a cell that relies
on a variable from a deleted or empty cell is reported without running the notebook
(which needs the EBRAINS data servers). Only undefined names are reported.

Usage: python .github/scripts/check_notebook_names.py [notebook ...]  (default: all tracked notebooks)
"""
import json
import re
import subprocess
import sys

from pyflakes.api import check
from pyflakes.messages import UndefinedLocal, UndefinedName
from pyflakes.reporter import Reporter

IPYTHON_BUILTINS = "display = get_ipython = None\n"


class Collect(Reporter):
    def __init__(self):
        self.messages = []

    def flake(self, message):
        if isinstance(message, (UndefinedName, UndefinedLocal)):
            self.messages.append(message)

    def syntaxError(self, filename, msg, lineno, offset, text):
        self.messages.append(f"line {lineno}: syntax error: {msg}")

    def unexpectedError(self, filename, msg):
        self.messages.append(msg)


def code_of(path):
    nb = json.load(open(path, encoding="utf-8"))
    cells = []
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            # IPython magics and shell escapes are not Python: keep the line count, drop the content
            cells.append(re.sub(r"(?m)^(\s*)[%!].*$", r"\1pass", source))
    return IPYTHON_BUILTINS + "\n".join(cells) + "\n"


def main():
    paths = sys.argv[1:] or subprocess.run(
        ["git", "ls-files", "*.ipynb"], capture_output=True, text=True, check=True
    ).stdout.splitlines()
    failed = False
    for path in paths:
        reporter = Collect()
        check(code_of(path), path, reporter)
        for message in reporter.messages:
            text = message.message % message.message_args if hasattr(message, "message_args") else message
            print(f"{path}: {text}")
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
