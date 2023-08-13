from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'demonslayer'
    __official_name__ = 'Kimetsu no Yaiba'
    __root_website__ = 'https://zerochan.net/Kimetsu+no+Yaiba'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

