#!/usr/bin/env python
from . import cli
from dotenvy import load_env, read_file
from os import path


__version__ = '0.1.0'


def main():
    if path.exists('.env'):
        load_env(read_file('.env'))

    cli.main(obj={})


if __name__ == '__main__':
    main()
