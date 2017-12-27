import click
import logging
import requests
import sys
try:
    import simplejson as json
except ImportError:
    import json
from sh import git, Command, ErrorReturnCode, CommandNotFound


DEFAULT_GITHUB_URL = 'https://api.github.com'
DEFAULT_CONTEXT = 'default'
DEFAULT_SUCCESS_MESSAGE = 'Tests pass!'
DEFAULT_PENDING_MESSAGE = 'Tests in progress'
DEFAULT_FAILURE_MESSAGE = 'Tests failed'
DEFAULT_ERROR_MESSAGE = 'Cannot run tests'
STATES = ['error', 'failure', 'pending', 'success']

is_interactive = sys.__stdin__.isatty()
log = logging.getLogger('ghstatus')
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s:%(levelname)s] %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


def lstrip(text, prefix):
    return text[len(prefix):] if text.startswith(prefix) else text


def rstrip(text, suffix):
    return text[:len(text) - len(suffix)] if text.endswith(suffix) else text


def get_repo():
    url = str(git('config', 'remote.origin.url')).strip()
    url = lstrip(url, 'git@github.com:')
    url = lstrip(url, 'https://github.com/')
    url = rstrip(url, '.git')
    return url


def get_sha():
    return str(git('rev-parse', 'HEAD')).strip()


@click.group()
@click.option('base_url', '--base-url', type=str, envvar='GITHUB_URL',
              default=DEFAULT_GITHUB_URL, show_default=True,
              help='GitHub API URL [env: GITHUB_URL]')
@click.option('username', '-u', type=str, envvar='GITHUB_USERNAME',
              help='GitHub API username [env: GITHUB_USERNAME]')
@click.option('password', '-p', type=str, envvar='GITHUB_PASSWORD',
              help='GitHub API password/token [env: GITHUB_PASSWORD]')
@click.option('repo', '--repo', envvar='GITHUB_REPO')
@click.option('sha', '--sha', envvar='GITHUB_SHA')
@click.pass_context
def main(ctx, base_url, username, password, repo, sha):
    ctx.obj['base_url'] = base_url
    ctx.obj['username'] = username
    ctx.obj['password'] = password
    ctx.obj['repo'] = repo
    ctx.obj['sha'] = sha


@main.command('exec')
@click.option('--context', default=DEFAULT_CONTEXT, show_default=True)
@click.option('--target-url', help='')
@click.option('--pending', default=DEFAULT_PENDING_MESSAGE,
              help='Pending message.')
@click.option('--success', default=DEFAULT_SUCCESS_MESSAGE,
              help='Success message.')
@click.option('--failure', default=DEFAULT_FAILURE_MESSAGE,
              help='Failure message.')
@click.option('--error', default=DEFAULT_ERROR_MESSAGE,
              help='Error message.')
@click.argument('command', nargs=-1)
@click.pass_context
def exe(ctx, context, target_url, pending, success, failure, error, command):
    def _status_set(state, description):
        log.info('%s -> %s', context, state)
        ctx.invoke(status_set, context=context, target_url=target_url,
                   state=state, description=description, silent=True)

    try:
        _status_set('pending', pending)
        cmd = Command(command[0])
        cmd = cmd.bake(command[1:]) if len(command) > 1 else cmd
        cmd(_fg=True)
        _status_set('success', success)
        exit(0)
    except ErrorReturnCode as e:
        log.error('Command failed with exit code: %d', e.exit_code)
        _status_set('failure', failure)
    except CommandNotFound as e:
        log.error('Command not found: %s', e)
        _status_set('error', error)
    except Exception as e:
        log.error(e, exc_info=True)
        _status_set('error', error)

    exit(1)


@main.command('set')
@click.option('--context', default=DEFAULT_CONTEXT, show_default=True)
@click.option('--description', help='Descriptive status message.')
@click.option('--target-url', help='URL to the status.')
@click.option('--silent', help='URL to the status.',
              is_flag=True, default=False)
@click.argument('state', type=click.Choice(STATES))
@click.pass_context
def status_set(ctx, state, context, description, target_url, silent):
    base_url = ctx.obj.get('base_url')
    username = ctx.obj.get('username')
    password = ctx.obj.get('password')
    repo = ctx.obj.get('repo') or get_repo()
    sha = ctx.obj.get('sha') or get_sha()
    status_url = '%s/repos/%s/statuses/%s' % (base_url, repo, sha)

    payload = {
        'context': context,
        'state': state,
        'description': description,
        'target_url': target_url,
    }

    r = requests.post(status_url, json=payload, auth=(username, password))
    if not silent:
        result = json.dumps(r.json(), indent=2)
        print(result)

    if r.status_code != 200 and not silent:
        exit(1)


@main.command('get')
@click.option('--context', default=DEFAULT_CONTEXT, show_default=True)
@click.option('json_output', '--json/--no-json', is_flag=True, default=True)
@click.pass_context
def status_get(ctx, context, json_output):
    base_url = ctx.obj.get('base_url')
    username = ctx.obj.get('username')
    password = ctx.obj.get('password')
    repo = ctx.obj.get('repo') or get_repo()
    sha = ctx.obj.get('sha') or get_sha()
    status_url = '%s/repos/%s/statuses/%s' % (base_url, repo, sha)

    r = requests.get(status_url, auth=(username, password))
    if json_output:
        print(json.dumps(r.json(), indent=2))
    else:
        for s in r.json():
            line = '[%s] %s - %s' % (s['context'], s['state'], s['description'])
            print(line)

    if r.status_code != 200:
        exit(1)