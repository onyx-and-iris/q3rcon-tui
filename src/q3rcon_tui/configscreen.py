from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from .settings import settings


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
