#!/usr/bin/env python3
"""Keep the tutorial notebooks free of outputs and environment-specific metadata.

The notebooks are stored without outputs so that diffs stay readable and nothing
from an author's machine (virtualenv names, Python versions, editor settings)
ends up in the repository. Rendered versions with outputs are built by CI.

Usage:
    python .github/scripts/clean_notebooks.py               # clean all tracked notebooks
    python .github/scripts/clean_notebooks.py a.ipynb ...   # clean the given notebooks
    python .github/scripts/clean_notebooks.py --check       # only report, exit 1 if unclean

Only the standard library is used, so it runs anywhere without installing anything.
"""
import argparse
import json
import pathlib
import subprocess
import sys

# A generic kernelspec, so Jupyter, Binder, Colab and EBRAINS Lab all pick their default Python kernel.
KERNELSPEC = {
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
    "name": "python3",
}
NOTEBOOK_METADATA = {"kernelspec": KERNELSPEC, "language_info": {"name": "python"}}

# Cell metadata worth keeping. "tags" are used by nbmake (e.g. "skip-execution",
# "raises-exception"); everything else (slideshow, collapsed, scrolled, execution
# timings, ...) is editor state.
KEEP_CELL_METADATA = {"tags"}


def clean(nb: dict) -> dict:
    nb["metadata"] = json.loads(json.dumps(NOTEBOOK_METADATA))
    for cell in nb["cells"]:
        cell["metadata"] = {
            k: v for k, v in cell.get("metadata", {}).items() if k in KEEP_CELL_METADATA
        }
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    return nb


def dumps(nb: dict) -> str:
    # Same layout as Jupyter/nbformat writes, so saving from Jupyter gives no spurious diff.
    return json.dumps(nb, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def tracked_notebooks() -> list:
    out = subprocess.run(
        ["git", "ls-files", "*.ipynb"], capture_output=True, text=True, check=True
    ).stdout
    return out.splitlines()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebooks", nargs="*", help="default: all notebooks tracked by git")
    parser.add_argument("--check", action="store_true", help="do not write; exit 1 if any notebook is unclean")
    args = parser.parse_args()

    unclean = []
    for path in map(pathlib.Path, args.notebooks or tracked_notebooks()):
        raw = path.read_text(encoding="utf-8")
        cleaned = dumps(clean(json.loads(raw)))
        if cleaned != raw:
            unclean.append(path)
            if not args.check:
                path.write_text(cleaned, encoding="utf-8")

    verb = "need cleaning" if args.check else "cleaned"
    for path in unclean:
        print(f"{verb}: {path}")
    if args.check and unclean:
        print("\nRun: python .github/scripts/clean_notebooks.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
