import json
import os
import re
from dataclasses import asdict, dataclass, field
from itertools import groupby
from subprocess import run
from urllib.parse import urlparse

from command import run_command

BROWSER_COMMAND = 'firefox-nightly'


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

    def to_string(self):
        return f'{self.prefix}.{self.window}.{self.id}\t{self.title}\t{self.url}'

    def full_id(self):
        return f'{self.prefix}.{self.window}.{self.id}'

    def activate(self):
        run(['bt', 'activate', self.full_id()])

    def open(self, url: str):
        return open_tab(f'{self.prefix}.{self.window}', url)

    def close(self):
        run(['bt', 'close', self.full_id()])

    def move(self, window: int):
        move_tabs_to_window([self], window)


def get_tabs_by_ids(tab_ids: list[str]):
    return [t for t in bt_list() if t.full_id() in tab_ids]


def move_tabs_to_window(tabs: list[Tab], window: int):
    tabs_before = bt_list()

    for t in tabs_before:
        if t in tabs:
            t.window = window
            print('Moving', t)

    stdin = '\n'.join(t.to_string() for t in tabs_before)

    run(
        ['bt', 'move'],
        env={
            **os.environ, 'EDITOR': './bt_editor.py'
        },
        input=stdin,
        text=True,
        check=True
    )


def tabs_by_window(tabs: list[Tab]):
    tabs = sorted(tabs, key=lambda t: (t.window, t))
    return {k: list(g) for k, g in groupby(tabs, lambda t: t.window)}


def tabs_by_domain(tabs: list[Tab]):
    tabs = sorted(tabs, key=lambda t: (t.url, t))
    return {k: list(g) for k, g in groupby(tabs, lambda t: url_domain(t.url))}


def url_domain(url: str):
    return urlparse(url).hostname


def bt_list_str():
    return run_command('bt list')


def bt_list_strs():
    '''Runs and returns standard output from "bt list"'''

    return bt_list_str().splitlines()


def bt_list():
    lines = bt_list_strs()
    return list(map(Tab.fromstring, lines))


def spawn_window():
    ids = {t.id for t in bt_list()}
    run([BROWSER_COMMAND])
    return next(t for t in bt_list() if t.id not in ids)


def serialize_tabs(tabs: list[Tab]):
    return json.dumps(list(map(asdict, sorted(tabs))))


def open_tab(prefix_window_id: str, url: str):
    run(['bt', 'open', prefix_window_id], input=url + '\n', text=True)


def close_tabs(tabs: list[Tab]):
    run(['bt', 'close'] + [t.full_id() for t in tabs])
