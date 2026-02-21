import re

from rich.table import Table
from rich.text import Text

from .settings import settings

Renderable = Text | Table | str


class Writable:
    RE_COLOR_CODES = re.compile(r'\^[0-9]')
    RE_MAP_FROM_STATUS = re.compile(r'^map: (?P<mapname>mp_[a-z_]+)$')
    RE_PLAYER_FROM_STATUS = re.compile(
        r'^\s*(?P<slot>[0-9]+)\s+'
        r'(?P<score>[0-9-]+)\s+'
        r'(?P<ping>[0-9]+)\s+'
        r'(?P<guid>[0-9a-f]+)\s+'
        r'(?P<name>.*?)\s+'
        r'(?P<last>[0-9]+?)\s*'
        r'(?P<ip>(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])):?'
        r'(?P<port>-?[0-9]{1,5})\s*'
        r'(?P<qport>-?[0-9]{1,5})\s+'
        r'(?P<rate>[0-9]+)$',
        re.IGNORECASE | re.VERBOSE,
    )
    RE_CVAR = re.compile(
        r'^["](?P<name>[a-z_]+)["]\sis[:]\s'
        r'["](?P<value>.*?)\^7["]\s'
        r'default[:]\s'
        r'["](?P<default>.*?)\^7["]\s'
        r'info[:]\s'
        r'["](?P<info>.*?)\^7["]$'
    )

    @staticmethod
    def remove_color_codes(s: str) -> str:
        return Writable.RE_COLOR_CODES.sub('', s)

    def parse(self, cmd, response: str, style=None) -> Renderable:
        response = response.removeprefix('print\n')
        if settings.raw:
            return Text(response, style=style)

        match cmd:
            case 'status':
                return self.status_table(response)
            case _:
                if m := self.RE_CVAR.match(response):
                    return self.cvar_table(m)
                else:
                    return Text(self.remove_color_codes(response), style=style)

    def error(self, message: str) -> Text:
        return Text(message, style='#c73d4b')

    def status_table(self, status_response: str) -> Table | str:
        table = Table(show_header=True, header_style='bold #88c0d0')
        table.add_column('Slot', justify='center')
        table.add_column('Score', justify='center')
        table.add_column('Ping', justify='center')
        table.add_column('GUID', justify='center')
        table.add_column('Name', justify='center')
        table.add_column('Last', justify='center')
        table.add_column('IP:Port', justify='center')
        table.add_column('QPort', justify='center')
        table.add_column('Rate', justify='center')

        mapname = 'unable to parse map name'
        for line in status_response.splitlines():
            if m := self.RE_PLAYER_FROM_STATUS.match(line):
                table.add_row(
                    m.group('slot'),
                    m.group('score'),
                    m.group('ping'),
                    m.group('guid'),
                    self.remove_color_codes(m.group('name')),
                    m.group('last'),
                    f'{m.group("ip")}:{m.group("port")}',
                    m.group('qport'),
                    m.group('rate'),
                )
            elif m := self.RE_MAP_FROM_STATUS.match(line):
                mapname = m.group('mapname')

        out = Text(f'Map: {mapname}\n', style='bold #88c0d0')
        if len(table.rows) == 0:
            return out.append('No players connected', style='#c73d4b')
        else:
            table.title = out
            return table

    def cvar_table(self, m: re.Match) -> Table:
        table = Table(show_header=True, header_style='bold #88c0d0')
        table.add_column('Name', justify='center')
        table.add_column('Value', justify='center')
        table.add_column('Default', justify='center')
        table.add_column('Info', justify='center')

        table.add_row(
            m.group('name'),
            self.remove_color_codes(m.group('value')),
            self.remove_color_codes(m.group('default')),
            self.remove_color_codes(m.group('info')),
        )

        return table
