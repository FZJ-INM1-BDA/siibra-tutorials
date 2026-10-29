# Contributing to siibra-tutorials

This page describes how the notebooks are kept clean, tested and published.
For running the tutorials, see the [README](https://github.com/FZJ-INM1-BDA/siibra-tutorials#readme).

## Notebooks are stored without outputs

Notebooks are committed without outputs, execution counts and environment-specific metadata
(kernel names of your virtual environment, Python version, editor settings). This keeps diffs readable
and nothing from your machine ends up in the repository.

Before committing, clean the notebooks with

```bash
python .github/scripts/clean_notebooks.py            # all notebooks
python .github/scripts/clean_notebooks.py my.ipynb   # only some
```

The script only uses the Python standard library. CI runs it with `--check` and fails if a notebook
still needs cleaning.

To clean notebooks automatically on every commit, install the optional [pre-commit](https://pre-commit.com)
hook once per clone:

```bash
pip install pre-commit    # or: uv tool install pre-commit
pre-commit install
pre-commit run --all-files   # try it on all notebooks
```

If the hook cleans a notebook, the commit is stopped: stage the cleaned notebook and commit again.
The hook runs the command given as `entry` in
[`.pre-commit-config.yaml`](https://github.com/FZJ-INM1-BDA/siibra-tutorials/blob/main/.pre-commit-config.yaml),
so that command must work outside an activated virtual environment, also from graphical clients such as
GitHub Desktop. `git commit --no-verify` skips the hook once.

## Adding a notebook

1. Start with a markdown cell with a title (`# ...`) and a short introduction.
2. Make the first code cell the commented-out setup cell used by all notebooks (copy it from an existing
   one) and list the packages your notebook needs. Packages that are not yet in
   [`requirements.txt`](https://github.com/FZJ-INM1-BDA/siibra-tutorials/blob/main/requirements.txt)
   must be added there too, since that is what Binder installs.
3. Use paths relative to the notebook. If the notebook writes files, add them to `.gitignore`.
4. Add a row to the table in the README. Copy an existing row and replace the notebook path in all three
   links (Binder, Colab, EBRAINS Lab).
5. Clean the notebook and check it (see below). CI tests every tracked `.ipynb` file automatically.

## Testing

The workflow
[test-tutorials.yml](https://github.com/FZJ-INM1-BDA/siibra-tutorials/blob/main/.github/workflows/test-tutorials.yml)
runs on every push to any branch, on pull requests from forks, and every Monday at 06:00 UTC. It

- checks that the notebooks are clean, and that no code cell uses a name that no earlier cell defines
  (with pyflakes, without running anything), and
- runs every notebook in its own job, with the Python version from `runtime.txt` (the one Binder uses)
  and the packages from `requirements.txt`, i.e. the latest siibra release.

The quick checks can be run locally before pushing:

```bash
python .github/scripts/clean_notebooks.py --check
pip install pyflakes
python .github/scripts/check_notebook_names.py
```

To run a notebook the way CI does:

```bash
pip install -r requirements.txt -r .github/requirements-tests.txt
python -m pytest --nbmake 01-BasicConcepts.ipynb
```

To test the notebooks with a development branch of siibra-python, open the workflow in the Actions tab,
choose *Run workflow* and enter the branch name.

The test tools in `.github/requirements-tests.txt` and the GitHub Actions (pinned by commit SHA) are kept
up to date by Dependabot, which skips releases younger than a week.

## Binder

[mybinder.org](https://mybinder.org) builds its environment from `runtime.txt` (Python version) and
`requirements.txt`. When raising the siibra version in `requirements.txt`, check that the new release
supports the Python version in `runtime.txt`; CI tests with that version, so a mismatch shows up there.
After a change to `main`, the first Binder launch rebuilds the image, which can take several minutes.

## The README is also the website

[fzj-inm1-bda.github.io/siibra-tutorials](https://fzj-inm1-bda.github.io/siibra-tutorials/) is built by
GitHub from the `main` branch on every push, and shows the README (this page is published there too).
Files under `.github/` are not published, so use absolute `https://github.com/...` links in the README and
here, not relative ones.
