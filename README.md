# q3rcon tui

[![Hatch project](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pypa/hatch/master/docs/assets/badge/v0.json)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI - Version](https://img.shields.io/pypi/v/q3rcon-tui.svg)](https://pypi.org/project/q3rcon-tui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/q3rcon-tui.svg)](https://pypi.org/project/q3rcon-tui)

-----

![img](./img/tui.png)

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

*with uv*

```console
uv tool install q3rcon-tui
```

*with pipx*

```console
pipx install q3rcon-tui
```

The TUI should now be discoverable as q3rcon-tui.

## Configuration

#### Flags

Pass `--host`, `--port` and `--password` as flags:

```console
q3rcon-tui --host=localhost --port=28960 --password=rconpassword
```

Additional flags:

-   `--raw`: Boolean flag, if set the RichLog will print raw responses without rendering tables.
-   `--min-status`: Boolean flag, if set the status command will print a minified table.
    -   note, this will have no effect if in *raw* mode.
-   `--append`: Boolean flag, if set the RichLog output will append each response continuously.
-   `--version`: Print the version of the TUI.
-   `--help`: Print the help message.

#### Environment Variables

Store and load from dotenv files located at:
-   .env in the cwd
-   user home directory / .config / q3rcon-tui / config.env

example .env:

```env
Q3RCON_TUI_HOST=localhost
Q3RCON_TUI_PORT=28960
Q3RCON_TUI_PASSWORD=rconpassword
Q3RCON_TUI_MIN_STATUS=false
Q3RCON_TUI_RAW=false
Q3RCON_TUI_APPEND=false
```

## Special Thanks

- [lapetus-11](https://github.com/Iapetus-11) for writing the [aio-q3-rcon](https://github.com/Iapetus-11/aio-q3-rcon) package.
- The developers at [Textualize](https://github.com/Textualize) for writing the [textual](https://github.com/Textualize/textual) package.

## License

`q3rcon-tui` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
