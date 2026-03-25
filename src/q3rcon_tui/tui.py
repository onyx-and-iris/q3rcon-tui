from aioq3rcon import Client, RCONError
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Input, RichLog

from .configscreen import ConfigScreen
from .settings import Settings
from .writable import Writable


class Q3RconTUI(App):
    CSS_PATH = 'q3rcon_tui.tcss'
    CMD_CONFIG = {
        'status': (2, 0.25, False),
        'fast_restart': (3, 1, True),
        'map_restart': (3, 1, True),
        'map': (3, 1, True),
        'map_rotate': (3, 1, True),
    }
    DEFAULT_TIMEOUT = 2
    DEFAULT_FRAGMENT_READ_TIMEOUT = 0.25

    def __init__(self):
        super().__init__()
        self._settings = Settings()
        self.writable = Writable(self)

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
        # prevent keypresses from ConfigScreen from triggering actions in RconApp
        if self.screen and isinstance(self.screen, ConfigScreen):
            return

        match event.key:
            case 'enter' if self.query_one('#command', Input).has_focus:
                self.query_one('#send', Button).press()
            case 'f2':
                self.query_one('#config', Button).press()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case 'quit':
                self._quit_button_handler()
            case 'config':
                await self._config_button_handler()
            case 'send':
                await self._send_button_handler()

    def _quit_button_handler(self):
        self.app.exit()

    async def _config_button_handler(self):
        result = await self.push_screen(ConfigScreen(self))
        if result:
            self.query_one('#response', RichLog).write(
                f'Configuration updated: {self._settings.host}:{self._settings.port}'
            )

    async def _send_button_handler(self):
        if not self._settings.append:
            self.query_one('#response', RichLog).clear()

        cmd = self.query_one('#command', Input).value.strip()
        if not cmd:
            self.app.bell()
            return

        timeout, fragment_read_timeout, interpret = Q3RconTUI.CMD_CONFIG.get(
            cmd.split()[0].lower(),
            (Q3RconTUI.DEFAULT_TIMEOUT, Q3RconTUI.DEFAULT_FRAGMENT_READ_TIMEOUT, False),
        )

        try:
            async with Client(
                self._settings.host,
                self._settings.port,
                self._settings.password,
                timeout=timeout,
                fragment_read_timeout=fragment_read_timeout,
            ) as client:
                response = await client.send_command(cmd, interpret=interpret)
                self.query_one('#response', RichLog).write(
                    self.writable.parse(cmd, response)
                )
        except RCONError:
            output = (
                f'Unable to execute command {cmd}.',
                'It may be due to a map change or a server restart.',
                'If the problem persists, please check your connection settings and ensure the server is running.',
            )
            self.query_one('#response', RichLog).write(
                self.writable.error('\n'.join(output))
            )

        self.query_one('#command', Input).value = ''


def main():
    app = Q3RconTUI()
    app.run()
