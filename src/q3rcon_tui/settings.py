from pathlib import Path
from typing import Annotated, Type

from pydantic import (
    AfterValidator,
    AliasChoices,
    BeforeValidator,
    Field,
)
from pydantic_settings import BaseSettings, CliSettingsSource, SettingsConfigDict

from .__about__ import __version__ as version


def version_callback(value: bool) -> bool | None:
    if value:
        print(f'q3rcon-tui version: {version}')
        raise SystemExit(0)
    return False


def is_valid_host(host: str) -> str | None:
    if not host:
        raise ValueError('Host cannot be empty')
    return host


def is_valid_port(port: int) -> int | None:
    if port < 1 or port > 65535:
        raise ValueError('Port must be between 1 and 65535')
    return port


def is_valid_password(password: str) -> str | None:
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    return password


class Settings(BaseSettings):
    host: Annotated[str, AfterValidator(is_valid_host)] = 'localhost'
    port: Annotated[int, AfterValidator(is_valid_port)] = 28960
    password: Annotated[str, AfterValidator(is_valid_password)] = ''
    append: bool = False
    min_status: bool = Field(
        default=False,
        alias='min-status',
        validation_alias=AliasChoices(
            'min-status',
            'Q3RCON_TUI_MIN_STATUS',
        ),
    )
    raw: bool = False
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
        validate_assignment=True,
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
