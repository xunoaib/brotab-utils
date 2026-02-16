import re
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


def wmctrl_list():
    out = run_command('wmctrl -lpGx')
    lines = out.strip().split('\n')
    pattern = r'^(\S+)\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s+([^\s]+)\s+([^\s]+)\s+(.+)$'

    for line in lines:
        m = re.match(pattern, line)
        assert m, 'Regex failed'

        window_id, *nums, wm_class, host, title = m.groups()
        desktop_id, pid, x, y, width, height = map(int, nums)

        window = Window(
            window_id, wm_class, host, title, desktop_id, pid, x, y, width,
            height
        )

        print(window)


if __name__ == '__main__':
    wmctrl_list()
