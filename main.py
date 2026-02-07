import json
import re
from dataclasses import asdict, dataclass, field
from itertools import groupby
from subprocess import PIPE, Popen, run
from typing import override
from urllib.parse import urlparse


@dataclass(order=True)
class Tab:
    prefix: str
    window: int
    id: int
    title: str
    url: str
    _line: str = field(repr=False)

    @staticmethod
    def fromstring(line: str):
        m = re.match(r'^(\S+)\.(\d+)\.(\d+)\t(.*)\t(.*?)$', line)
        assert m, f'Unknown format: {line!r}'
        prefix, window, _id, title, url = m.groups()
        return Tab(prefix, int(window), int(_id), title, url, line)

    @staticmethod
    def fromid(prefix_window_id: str):
        m = re.match(r'^(\S+)\.(\d+)\.(\d+)$', prefix_window_id)
        assert m, f'Unknown format: {prefix_window_id!r}'
        prefix, window, _id, = m.groups()
        return Tab(prefix, int(window), int(_id), '', '', '')

    def identifier(self):
        return f'{self.prefix}.{self.window}.{self.id}'

    def activate(self):
        run(['bt', 'activate', self.identifier()])

    def open(self, url: str):
        return open_tab(f'{self.prefix}.{self.window}', url)


def tabs_by_window(tabs: list[Tab]):
    tabs = sorted(tabs, key=lambda t: (t.window, t))
    return {k: list(g) for k, g in groupby(tabs, lambda t: t.window)}


def tabs_by_domain(tabs: list[Tab]):
    tabs = sorted(tabs, key=lambda t: (t.url, t))
    return {k: list(g) for k, g in groupby(tabs, lambda t: url_domain(t.url))}


def url_domain(url: str):
    return urlparse(url).hostname


def bt_list_strs(error_on_stderr=True):
    '''Runs and returns standard output from "bt list"'''

    out, err = Popen(
        ['bt list'],
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    ).communicate()

    if err:
        print(f'\033[91mSTDERR: {err.decode()}\033[0m')
        if error_on_stderr:
            raise ValueError(f'Error running "bt list": {err.decode()}')

    return out.decode().splitlines()


def bt_list(error_on_stderr=True):
    lines = bt_list_strs(error_on_stderr)
    return list(map(Tab.fromstring, lines))


def spawn_window():
    ids = {t.id for t in bt_list()}
    run(['firefox'])
    return next(t for t in bt_list() if t.id not in ids)


def serialize_tabs(tabs: list[Tab]):
    return json.dumps(list(map(asdict, sorted(tabs))))


def open_tab(prefix_window_id: str, url: str):
    run(['bt', 'open', prefix_window_id], input=url + '\n', text=True)


def main():
    tabs = bt_list()

    a = spawn_window()
    # b = spawn_window()

    a.open('http://duckduckgo.com')

    exit()

    groups = tabs_by_window(tabs)
    groups = tabs_by_domain(tabs)

    for key, group in groups.items():
        print('>>>', key)
        for t in group:
            print(t.url)
        print()


if __name__ == '__main__':
    main()
