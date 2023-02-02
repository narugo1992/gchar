import os
import pathlib

META_FILE = os.path.abspath(os.path.join('gchar', 'config', 'meta.py'))
assert os.path.exists(META_FILE)

from gchar.config.meta import __VERSION__

if __name__ == '__main__':
    print(f'Reading {META_FILE!r} ...')
    meta_txt = pathlib.Path(META_FILE).read_text()

    print(f'Cracking version information ...')
    version_tuple = tuple(map(int, __VERSION__.split('.')))
    assert len(version_tuple) == 3
    new_version_tuple = (*version_tuple[:-1], version_tuple[-1] + 1)
    new_version = '.'.join(map(str, new_version_tuple))

    print(f'Updating {__VERSION__!r} --> {new_version!r} ...')
    new_meta_txt = meta_txt.replace(__VERSION__, new_version)

    print(f'Writing to {META_FILE!r} ...')
    pathlib.Path(META_FILE).write_text(new_meta_txt)
