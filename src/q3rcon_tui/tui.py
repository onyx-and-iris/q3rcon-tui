import re
from pathlib import Path
from typing import Annotated, Type

from aioq3rcon import Client, RCONError
from loguru import logger
from pydantic import AfterValidator, BeforeValidator
from pydantic_settings import BaseSettings, CliSettingsSource, SettingsConfigDict
from textual.app import App, ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RichLog, Static

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
        # Allow field assignment for runtime updates
        validate_assignment=False,
        frozen=False,
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


class ConfigScreen(ModalScreen[bool]):
    """Modal dialog for configuring connection settings."""

    def __init__(self, current_host: str, current_port: int, current_password: str):
        super().__init__()
        self.current_host = current_host
        self.current_port = current_port
        self.current_password = current_password

    def compose(self) -> ComposeResult:
        with Vertical(id='config-dialog'):
            yield Static('Connection Configuration', id='config-title')
            with Vertical(id='config-form'):
                yield Label('Host:')
                yield Input(
                    value=self.current_host, placeholder='localhost', id='host-input'
                )
                yield Label('Port:')
                yield Input(
                    value=str(self.current_port), placeholder='28960', id='port-input'
                )
                yield Label('Password:')
                yield Input(
                    value=self.current_password,
                    placeholder='Enter password',
                    password=True,
                    id='password-input',
                )
            with Horizontal(id='config-buttons'):
                yield Button('Save', variant='success', id='config-save')
                yield Button('Cancel', variant='error', id='config-cancel')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'config-save':
            try:
                new_host = (
                    self.query_one('#host-input', Input).value.strip() or 'localhost'
                )
                new_port = int(self.query_one('#port-input', Input).value or '28960')
                new_password = self.query_one('#password-input', Input).value

                if new_port < 1 or new_port > 65535:
                    raise ValueError('Port must be between 1 and 65535')

                if len(new_password) < 8:
                    raise ValueError('Password must be at least 8 characters long')

                settings.host = new_host
                settings.port = new_port
                settings.password = new_password

                self.dismiss(True)
            except ValueError:
                self.app.bell()
        elif event.button.id == 'config-cancel':
            self.dismiss(False)


class RconApp(App):
    RE_COLOR_CODES = re.compile(r'\^[0-9]')
    CSS_PATH = 'rcon_tui.tcss'

    def compose(self) -> ComposeResult:
        yield Grid(
            Input('status', placeholder='Enter a rcon command', id='command'),
            RichLog(id='response'),
            Button('Send', variant='success', id='send'),
            Button('Config', variant='warning', id='config'),
            Button('Quit', variant='primary', id='quit'),
            id='dialog',
        )

    async def on_key(self, event) -> None:
        match event.key:
            case 'enter' if self.query_one('#command', Input).has_focus:
                self.query_one('#send', Button).press()
            case 'f2':
                self.query_one('#config', Button).press()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'quit':
            self.app.exit()
        elif event.button.id == 'config':
            result = await self.push_screen(
                ConfigScreen(settings.host, settings.port, settings.password)
            )
            if result:
                self.query_one('#response', RichLog).write(
                    f'Configuration updated: {settings.host}:{settings.port}'
                )
            return

        if event.button.id != 'send':
            return

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
