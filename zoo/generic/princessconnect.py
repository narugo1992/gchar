from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'princessconnect'
    __official_name__ = 'Princess Connect'
    __root_website__ = 'https://zerochan.net/Princess+Connect'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

