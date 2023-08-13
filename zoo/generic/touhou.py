from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'touhou'
    __official_name__ = 'Touhou'
    __root_website__ = 'https://zerochan.net/Touhou'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

