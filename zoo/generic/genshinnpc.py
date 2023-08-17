from gchar.games.genshin import Character as GenshinCharacter
from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'genshinnpc'
    __official_name__ = 'Genshin Impact'
    __root_website__ = 'https://zerochan.net/Genshin+Impact'
    __exclude_cls__ = GenshinCharacter


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
