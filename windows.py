import re
from collections import defaultdict
from dataclasses import dataclass

from command import run_command


@dataclass
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


@dataclass
class Desktop:
    index: int
    active: bool
    dg: str
    vp_x: int
    vp_y: int
    wa: str
    desktop_id: int


def wmctrl_list():
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


def wmctrl_desktops():
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


if __name__ == '__main__':

    windows = wmctrl_list()
    desktops = {d.desktop_id: d for d in wmctrl_desktops()}

    windows_by_desktop = defaultdict(list)

    for window in windows:
        windows_by_desktop[window.desktop_id].append(window)

    for did, windows in windows_by_desktop.items():
        print(desktops[did])
        print()
        for w in windows:
            print(f'   {w.title}')
        print()
