import re
from dataclasses import dataclass, field
from subprocess import PIPE, Popen


@dataclass
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


def next_interval(now: float, interval: int):
    return now - (now % interval) + interval


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


def main():
    tabs = bt_list()

    for t in tabs:
        print(t)


if __name__ == '__main__':
    main()
