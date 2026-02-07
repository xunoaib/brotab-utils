#!/usr/bin/env python3
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print('Expected temp filename', file=sys.stderr)
        sys.exit(1)

    Path(sys.argv[1]).write_text(sys.stdin.read())


if __name__ == '__main__':
    main()
