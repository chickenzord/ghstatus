ghstatus
========

.. image:: https://img.shields.io/travis/chickenzord/ghstatus.svg?style=flat-square
    :target: https://travis-ci.org/chickenzord/ghstatus
    :alt: Build status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://raw.githubusercontent.com/chickenzord/ghstatus/master/LICENSE.txt
    :alt: MIT license

.. image:: https://img.shields.io/pypi/v/ghstatus.svg?style=flat-square
    :target: https://pypi.python.org/pypi/ghstatus
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/ghstatus.svg?style=flat-square
    :target: https://pypi.python.org/pypi/ghstatus
    :alt: PyPI python version


GitHub commit status notifier CLI


Options
-------

These options can be automatically set from env variables or dotenv (.env) file in working dir.

- `-u`: `GITHUB_USERNAME`
- `-p`: `GITHUB_PASSWORD`
- `--base-url`: `GITHUB_URL`
- `--repo`: `GITHUB_REPO`
- `--sha`: `GITHUB_SHA`
- `--target-url`: `TARGET_URL`

These options can be set automatically in Jenkins context (`JENKINS_URL` is set).

- `--target-url`: `BUILD_URL`

If not set by either CLI args or env variables,
these options can be automatically detected from git repository in current working dir.

- `--repo`: inferred from `.git/config`
- `--sha`: inferred by executing `git rev-parse HEAD` internally


Sample commands
---------------

**get all statuses** ::

  ghstatus get

**set status** ::

  ghstatus set success --context=unit-test --description='All tests pass!' \
    --target-url=https://example.com/my-test/1

**set status dynamically based on command exit code** ::

  ghstatus exec --context=unit-test -- ./gradlew test
