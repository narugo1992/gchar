from gchar.games.arknights import Character as ArknightsCharacter
from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'arknightsnpc'
    __official_name__ = 'Arknights'
    __root_website__ = 'https://zerochan.net/Arknights'
    __exclude_cls__ = ArknightsCharacter


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
