#!/usr/bin/env python
from . import cli
from dotenvy import load_env, read_file
from os import environ, path


__version__ = '0.2.3'


def jenkins_autoset():
    if 'JENKINS_URL' not in environ:
        return

    environ.setdefault('TARGET_URL', environ.get('BUILD_URL'))


def main():
    if path.exists('.env'):
        load_env(read_file('.env'))

    jenkins_autoset()

    cli.main(obj={})


if __name__ == '__main__':
    main()
