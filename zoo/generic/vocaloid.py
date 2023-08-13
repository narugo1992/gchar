from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'vocaloid'
    __official_name__ = 'VOCALOID'
    __root_website__ = 'https://zerochan.net/VOCALOID'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

