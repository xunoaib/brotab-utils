from subprocess import PIPE, Popen


def run_command(command: str, error_on_stderr=True):
    out, err = Popen(
        [command],
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    ).communicate()

    if err:
        print(f'\033[91mSTDERR: {err.decode()}\033[0m')
        if error_on_stderr:
            raise ValueError(f'Error running "bt list": {err.decode()}')

    return out.decode()
