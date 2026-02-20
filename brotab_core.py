import json
import os
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from itertools import groupby
from subprocess import run
from urllib.parse import urlparse

from command import run_command

BROWSER_COMMAND = os.getenv('BROWSER_COMMAND', 'firefox-nightly')


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
        return next(t for t in bt_list() if t.full_id() == prefix_window_id)

    @staticmethod
    def fromids(prefix_window_ids: Iterable[str]):
        '''Faster bulk version of fromid'''
        tabs = {t.full_id(): t for t in bt_list()}
        return [tabs[id] for id in prefix_window_ids]

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

    @property
    def loaded(self):
        return not self.title.startswith('💤 ')


@dataclass
class ActiveTab:
    tab_id: str
    client: str
    hostport: str
    unknown_id: int
    browser: str


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


def bt_list():
    lines = run_command('bt list').splitlines()
    return list(map(Tab.fromstring, lines))


def _bt_active():
    lines = run_command('bt active').splitlines()

    active: list[ActiveTab] = []
    for line in lines:
        tab_id, client, hostport, pid, browser = line.split('\t')
        active.append(ActiveTab(tab_id, client, hostport, int(pid), browser))

    return active


def bt_active():
    return Tab.fromids({t.tab_id for t in _bt_active()})


def spawn_window():
    ids = {t.id for t in bt_list()}
    run([BROWSER_COMMAND])
    return next(t for t in bt_list() if t.id not in ids)


def serialize_tabs(tabs: list[Tab]):
    return json.dumps(list(map(asdict, sorted(tabs))))


def open_tab(prefix_window_id: str, url: str):
    result = run(
        ['bt', 'open', prefix_window_id],
        input=url + '\n',
        text=True,
        capture_output=True
    )
    return Tab.fromid(result.stdout.strip())


def close_tabs(tabs: list[Tab]):
    run(['bt', 'close'] + [t.full_id() for t in tabs])
