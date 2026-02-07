from subprocess import PIPE, Popen


def next_interval(now: float, interval: int):
    return now - (now % interval) + interval


def bt_list_str(error_on_stderr=True):
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

    return out.decode()


def main():
    out = bt_list_str()
    print(out)


if __name__ == '__main__':
    main()
