import mimetypes
import os
import re
from functools import partial

import click
from ditk import logging
from hbutils.system import urlsplit
from hfmirror.resource import SyncResource
from hfmirror.storage import HuggingfaceStorage
from hfmirror.sync import SyncTask
from huggingface_hub import HfApi, configure_http_backend
from tqdm.auto import tqdm

from gchar.games.dispatch.access import GAME_CHARS
from gchar.generic import import_generic
from gchar.utils import GLOBAL_CONTEXT_SETTINGS, srequest, get_requests_session
from gchar.utils import print_version as _origin_print_version

configure_http_backend(partial(get_requests_session, timeout=60))

import_generic()


class SkinResource(SyncResource):
    def __init__(self, chs, ch_type):
        SyncResource.__init__(self)
        self.characters = chs
        self.ch_type = ch_type
        self.session = get_requests_session(timeout=60)

    def grab(self):
        yield 'metadata', {'game': self.ch_type.__game_name__}, ''
        _exist_ids = set()
        for ch in tqdm(self.characters):
            if ch.index in _exist_ids:
                continue

            metadata = {
                'id': ch.index,
                'cnname': str(ch.cnname) if ch.cnname else None,
                'jpname': str(ch.jpname) if ch.jpname else None,
                'enname': str(ch.enname) if ch.enname else None,
                'alias': list(map(str, ch.alias_names)),
            }
            yield 'metadata', metadata, f'{ch.index}'
            _exist_ids.add(ch.index)

            for skin_ in ch.skins:
                _, ext_ = os.path.splitext(urlsplit(skin_.url).filename)
                if not ext_:
                    resp_ = srequest(self.session, 'HEAD', skin_.url)
                    ext_ = mimetypes.guess_extension(resp_.headers['Content-Type'])

                filename_ = re.sub(r'\W+', '_', skin_.name).strip('_') + ext_
                yield 'remote', skin_.url, f'{ch.index}/{filename_}', {'name': skin_.name}


print_version = partial(_origin_print_version, 'gchar')


@click.command(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Download all the skins of a game.')
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.option('--game', '-g', 'game', type=click.Choice(sorted(GAME_CHARS.keys())), required=True,
              help='Game to download all images.', show_default=True)
@click.option('--repo', '-r', 'repo', type=str, default=None,
              help='Repository to upload.', show_default=True)
def cli(game, repo):
    logging.try_init_root(logging.INFO)
    ch_class = GAME_CHARS[game]
    resource = SkinResource(ch_class.all(), ch_class)

    repo = repo or ch_class.__skin_repository__
    api = HfApi(token=os.environ['HF_TOKEN'])
    api.create_repo(repo, repo_type='dataset', exist_ok=True)
    storage = HuggingfaceStorage(repo=repo, hf_client=api, namespace=game)

    task = SyncTask(resource, storage)
    task.sync()


if __name__ == '__main__':
    cli()  # pragma: no cover
