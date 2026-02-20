import re

from rich.table import Table

from .settings import settings


class Writable:
    RE_COLOR_CODES = re.compile(r'\^[0-9]')
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

    def parse(self, cmd, response: str) -> str:
        response = response.removeprefix('print\n')
        if settings.raw:
            return response

        match cmd:
            case 'status':
                return self.status_table(response)
            case _:
                match self.RE_CVAR.match(response):
                    case None:
                        return self.remove_color_codes(response)
                    case m:
                        return self.cvar_table(m)

    def status_table(self, status_response: str) -> Table | str:
        table = Table(show_header=True, header_style='bold #88c0d0')
        table.add_column('Slot', justify='center')
        table.add_column('Score', justify='center')
        table.add_column('Ping', justify='center')
        table.add_column('GUID', justify='center')
        table.add_column('Name', justify='center')
        table.add_column('Last', justify='center')
        table.add_column('IP', justify='center')
        table.add_column('Port', justify='center')
        table.add_column('QPort', justify='center')
        table.add_column('Rate', justify='center')

        for line in status_response.splitlines():
            match self.RE_PLAYER_FROM_STATUS.match(line):
                case None:
                    continue
                case m:
                    table.add_row(
                        m.group('slot'),
                        m.group('score'),
                        m.group('ping'),
                        m.group('guid'),
                        self.remove_color_codes(m.group('name')),
                        m.group('last'),
                        m.group('ip'),
                        m.group('port'),
                        m.group('qport'),
                        m.group('rate'),
                    )

        if len(table.rows) == 0:
            return 'No players connected.'
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
