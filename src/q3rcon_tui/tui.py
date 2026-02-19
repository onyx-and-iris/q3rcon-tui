import re
from pathlib import Path
from typing import Annotated, Type

from aioq3rcon import Client, RCONError
from loguru import logger
from pydantic import AfterValidator, BeforeValidator
from pydantic_settings import BaseSettings, CliSettingsSource, SettingsConfigDict
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Input, RichLog

from .__about__ import __version__ as version


def is_valid_password(password: str) -> str | None:
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    return password


def version_callback(value: bool) -> bool | None:
    if value:
        print(f'q3rcon-tui version: {version}')
        raise SystemExit(0)
    return False


class Settings(BaseSettings):
    host: str = 'localhost'
    port: int = 28960
    password: Annotated[str, AfterValidator(is_valid_password)] = ''
    refresh_output: bool = False
    version: Annotated[bool, BeforeValidator(version_callback)] = False

    model_config = SettingsConfigDict(
        env_file=(
            '.env',
            Path.home() / '.config' / 'q3rcon-tui' / 'config.env',
        ),
        env_file_encoding='utf-8',
        env_prefix='Q3RCON_TUI_',
        cli_prefix='',
        cli_parse_args=True,
        cli_implicit_flags=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: ...,
        env_settings: ...,
        dotenv_settings: ...,
        file_secret_settings: ...,
    ) -> tuple:
        return (
            CliSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            init_settings,
        )


try:
    settings = Settings()
except ValueError as e:
    logger.error(e)
    raise SystemExit(1)


class RconApp(App):
    RE_COLOR_CODES = re.compile(r'\^[0-9]')
    CSS_PATH = 'rcon_tui.tcss'

    def compose(self) -> ComposeResult:
        yield Grid(
            Input('status', placeholder='Enter a rcon command', id='command'),
            RichLog(id='response'),
            Button('Send', variant='error', id='send'),
            Button('Quit', variant='primary', id='quit'),
            id='dialog',
        )

    async def on_key(self, event) -> None:
        if event.key == 'enter':
            if self.query_one('#command', Input).has_focus:
                self.query_one('#send', Button).press()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'quit':
            self.app.exit()

        if settings.refresh_output:
            self.query_one('#response', RichLog).clear()

        try:
            async with Client(
                settings.host, settings.port, settings.password
            ) as client:
                response = await client.send_command(
                    self.query_one('#command', Input).value
                )
                self.query_one('#response', RichLog).write(
                    self.remove_color_codes(response.removeprefix('print\n'))
                )
        except RCONError as e:
            self.query_one('#response', RichLog).write(
                f'{type(e).__name__}: Unable to connect to server: is the server running and are the host, port, and password correct? ({e})'
            )

        self.query_one('#command', Input).value = ''

    @staticmethod
    def remove_color_codes(s: str) -> str:
        return RconApp.RE_COLOR_CODES.sub('', s)


def main():
    app = RconApp()
    app.run()
