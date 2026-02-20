from aioq3rcon import Client, RCONError
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Input, RichLog

from .configscreen import ConfigScreen
from .settings import settings
from .writable import Writable


class RconApp(App):
    CSS_PATH = 'q3rcon_tui.tcss'

    def __init__(self):
        super().__init__()
        self.writable = Writable()

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

        if not settings.append:
            self.query_one('#response', RichLog).clear()

        try:
            async with Client(
                settings.host, settings.port, settings.password
            ) as client:
                cmd = self.query_one('#command', Input).value.strip()
                if not cmd:
                    self.app.bell()
                    return
                response = await client.send_command(cmd)
                self.query_one('#response', RichLog).write(
                    self.writable.parse(cmd, response)
                )
        except RCONError as e:
            self.query_one('#response', RichLog).write(
                f'{type(e).__name__}: Unable to connect to server: is the server running and are the host, port, and password correct? ({e})'
            )

        self.query_one('#command', Input).value = ''


def main():
    app = RconApp()
    app.run()
