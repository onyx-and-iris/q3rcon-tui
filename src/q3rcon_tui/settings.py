from pathlib import Path
from typing import Annotated, Type

from loguru import logger
from pydantic import AfterValidator, BeforeValidator
from pydantic_settings import BaseSettings, CliSettingsSource, SettingsConfigDict

from .__about__ import __version__ as version


def version_callback(value: bool) -> bool | None:
    if value:
        print(f'q3rcon-tui version: {version}')
        raise SystemExit(0)
    return False


def is_valid_password(password: str) -> str | None:
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    return password


class Settings(BaseSettings):
    host: str = 'localhost'
    port: int = 28960
    password: Annotated[str, AfterValidator(is_valid_password)] = ''
    append: bool = False
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
