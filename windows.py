import re
from collections import defaultdict
from dataclasses import dataclass

from brotab_core import bt_active
from command import run_command


@dataclass(order=True, frozen=True)
class Window:
    window_id: str
    wm_class: str
    host: str
    title: str
    desktop_id: int
    pid: int
    x: int
    y: int
    width: int
    height: int


@dataclass(order=True, frozen=True)
class Desktop:
    index: int
    active: bool
    dg: str
    vp_x: int
    vp_y: int
    wa: str
    desktop_id: int


def wmctrl_list() -> list[Window]:
    out = run_command('wmctrl -lpGx')
    lines = out.strip().split('\n')
    pattern = r'^(\S+)\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s+([^\s]+)\s+([^\s]+)\s+(.+)$'

    windows = []
    for line in lines:
        m = re.match(pattern, line)
        assert m, 'Regex failed'

        window_id, *nums, wm_class, host, title = m.groups()
        desktop_id, pid, x, y, width, height = map(int, nums)

        window = Window(
            window_id, wm_class, host, title, desktop_id, pid, x, y, width,
            height
        )
        windows.append(window)

    return windows


def wmctrl_desktops() -> list[Desktop]:
    out = run_command('wmctrl -d')
    lines = out.strip().split('\n')
    pattern = r'^(\d+)\s+([-*])\s+DG:\s+(\S+)\s+VP:\s+(\d+),(\d+)\s+WA:\s+(\S+)\s+(\d+)$'

    desktops = []

    for line in lines:
        m = re.match(pattern, line)
        assert m, 'Regex failed'
        index, active, dg, vp_x, vp_y, wa, desktop_id = m.groups()

        desktop = Desktop(
            int(index),
            active == '*',
            dg,
            int(vp_x),
            int(vp_y),
            wa,
            int(desktop_id),
        )
        desktops.append(desktop)

    return desktops


def find_window_tabs(
    windows: list[Window] | None = None,
    WIN_TITLE_REPLACE=' — Firefox Nightly'
):
    '''Find brotab tab associated with each active browser window'''

    if match_all := windows is None:
        windows = wmctrl_list()

    window_titles = defaultdict(list)
    for window in windows:
        title = window.title.replace(WIN_TITLE_REPLACE, '')
        window_titles[title].append(window)

    window_tabs = {}
    for tab in bt_active():
        windows = window_titles[tab.title]

        if len(windows) == 1:
            window_tabs[windows[0]] = tab
        elif len(windows) == 0 and not match_all:
            pass
        else:
            raise ValueError(
                f'ERROR: Expected one window, found {len(windows)} for {tab.title!r}'
            )

    return dict(sorted(list(window_tabs.items())))


if __name__ == '__main__':

    desktops = {d.desktop_id: d for d in wmctrl_desktops()}

    desktop_windows = defaultdict(list)
    for window in wmctrl_list():
        desktop_windows[window.desktop_id].append(window)

    window_tabs = find_window_tabs()

    for did, windows in desktop_windows.items():
        print(desktops[did])
        print()
        for w in windows:
            if tabs := window_tabs.get(w):
                print(f'    {tabs}')
            else:
                print(f'   {w.title}')
        print()
