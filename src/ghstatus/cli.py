import click
import requests
try:
    import simplejson as json
except ImportError:
    import json
from sh import git


DEFAULT_GITHUB_URL = 'https://api.github.com'
DEFAULT_CONTEXT = 'default'
STATES = ['error', 'failure', 'pending', 'success']


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


@main.command()
@click.option('--context', default=DEFAULT_CONTEXT, show_default=True)
@click.option('--description')
@click.option('--target-url')
@click.argument('state', type=click.Choice(STATES))
@click.pass_context
def set(ctx, state, context, description, target_url):
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

    print(locals())

    r = requests.post(status_url, json=payload, auth=(username, password))
    click.echo(json.dumps(r.json(), indent=2))


@main.command()
@click.option('--context', default=DEFAULT_CONTEXT, show_default=True)
@click.option('json_output', '--json/--no-json', is_flag=True, default=True)
@click.pass_context
def get(ctx, context, json_output):
    base_url = ctx.obj.get('base_url')
    username = ctx.obj.get('username')
    password = ctx.obj.get('password')
    repo = ctx.obj.get('repo') or get_repo()
    sha = ctx.obj.get('sha') or get_sha()
    status_url = '%s/repos/%s/statuses/%s' % (base_url, repo, sha)

    r = requests.get(status_url, auth=(username, password))
    if json_output:
        click.echo(json.dumps(r.json(), indent=2))
    else:
        for s in r.json():
            line = '[%s] %s - %s' % (s['context'], s['state'], s['description'])
            click.echo(line)

    if r.status_code != 200:
        exit(1)
