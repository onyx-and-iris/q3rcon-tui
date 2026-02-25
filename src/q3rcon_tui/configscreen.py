from pydantic import ValidationError
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class ConfigScreen(ModalScreen[bool]):
    """Modal dialog for configuring connection settings."""

    def __init__(self, tui):
        super().__init__()
        self._settings = tui._settings
        self._original_settings = self._settings.model_copy()

    def compose(self) -> ComposeResult:
        with Vertical(id='config-dialog'):
            yield Static('Connection Configuration', id='config-title')
            with Vertical(id='config-form'):
                yield Label('Host:')
                yield Input(
                    value=self._original_settings.host,
                    placeholder='localhost',
                    id='host-input',
                )
                yield Label('Port:')
                yield Input(
                    value=str(self._original_settings.port),
                    placeholder='28960',
                    id='port-input',
                )
                yield Label('Password:')
                yield Input(
                    value=self._original_settings.password,
                    placeholder='Enter password',
                    password=True,
                    id='password-input',
                )
            with Horizontal(id='config-buttons'):
                yield Button('Save', variant='success', id='config-save')
                yield Button('Cancel', variant='error', id='config-cancel')

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'config-save':
                self._save_button_handler()
            case 'config-cancel':
                self._cancel_button_handler()

    def _save_button_handler(self):
        self._clear_field_errors()

        try:
            new_host = self.query_one('#host-input', Input).value.strip() or 'localhost'
            new_port = self.query_one('#port-input', Input).value
            new_password = self.query_one('#password-input', Input).value

            try:
                new_port = int(new_port or '28960')
            except ValueError:
                self._show_field_error('port-input', 'Port must be a valid number')
                return

            self._settings.host = new_host
            self._settings.port = new_port
            self._settings.password = new_password

            self.dismiss(True)
        except ValidationError as e:
            for error in e.errors():
                field_name = error.get('loc', ())
                error_msg = error.get('msg', str(error))

                match field_name:
                    case ('host',):
                        self._show_field_error('host-input', error_msg)
                    case ('port',):
                        self._show_field_error('port-input', error_msg)
                    case ('password',):
                        self._show_field_error('password-input', error_msg)
                break  # Only show the first error

    def _show_field_error(self, field_id: str, error_message: str):
        """Show error message in the specified input field."""
        self._clear_field_errors()

        field = self.query_one(f'#{field_id}', Input)
        field.add_class('error')
        field.value = ''

        field.placeholder = error_message
        field.focus()

        self.app.bell()

    def _clear_field_errors(self):
        """Clear error styling from all input fields."""
        for field_id in ['host-input', 'port-input', 'password-input']:
            field = self.query_one(f'#{field_id}', Input)
            field.remove_class('error')

            match field_id:
                case 'host-input':
                    field.placeholder = 'localhost'
                case 'port-input':
                    field.placeholder = '28960'
                case 'password-input':
                    field.placeholder = 'Enter password'

    def _cancel_button_handler(self):
        self.dismiss(False)
