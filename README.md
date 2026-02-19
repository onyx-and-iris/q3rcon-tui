# q3rcon tui

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
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

#### Environment Variables

Store and load from dotenv files located at:
-   .env in the cwd
-   user home directory / .config / rcon-tui / config.env

example .env:

```bash
Q3RCON_TUI_HOST=localhost
Q3RCON_TUI_PORT=28960
Q3RCON_TUI_PASSWORD=rconpassword
Q3RCON_TUI_REFRESH_OUTPUT=true
```

## License

`q3rcon-tui` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
