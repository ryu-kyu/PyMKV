# PyMKV

## Getting Started

To get started, make sure you have [Poetry](https://python-poetry.org/docs/#installation) installed.

Next, run the below commands to setup and spawn `venv` shell via Poetry:

```shell
poetry install
poetry shell
```

To run a specific script, type in below Poetry command:

```shell
poetry run pymkv/<script_name>.py
```

### Additional Notes

`eps.txt` is by default the naming scheme for batch list of filenames to rename mkv files to.

-   This file is ignored by `.gitignore`. So, if you have a new environment, create it via `touch eps.txt`
