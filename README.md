# Discord Web client

The Discord web client as a Google Chrome windowed application.

Current assumptions:

- DE makes use of `.desktop` files
- `$HOME/.local/bin` is on `PATH`
- A `discord` icon is available at `$XDG_DATA_HOME/icons/`
- All four Chrome release channels still support `--app`

This list is unlikely to be exhaustive. If you find an assumption that is worth mentioning, please submit a merge request.

## Installation

Simply run `./install.py`.
Help is available with `--help`.

## Uninstallation

`./uninstall.py` will take care of it.
