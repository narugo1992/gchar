import subprocess
import sys

import pandas as pd
from hbutils.string import plural_word
from hbutils.system import urlsplit
from tqdm.auto import tqdm

from gchar.games import list_available_game_names, get_character_class


def _get_sites(game):
    p = subprocess.run([sys.executable, '-m', f'zoo.games.{game}', 'sites'], stdout=subprocess.PIPE)
    p.check_returncode()

    retval = []
    for site in p.stdout.decode().splitlines(keepends=False):
        site = site.strip()
        if not site:
            continue

        host = urlsplit(site).host
        short_host = '.'.join(host.split('.')[-2:])
        retval.append((short_host, site))

    return retval


if __name__ == '__main__':
    print(f'The following {plural_word(len(list_available_game_names()), "game")} are supported:')
    print()

    columns = ['Game', 'Official\nName', 'Data\nSources']
    data = []
    for name in tqdm(list_available_game_names()):
        ds_text = ', '.join([
            f'`{site_name} <{site_url}>`_'
            for site_name, site_url in _get_sites(name)
        ])
        data.append((name, get_character_class(name).__official_name__, ds_text))

    df = pd.DataFrame(columns=columns, data=data)
    print(df.to_markdown(headers='keys', tablefmt='rst', index=False))
