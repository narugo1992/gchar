from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'violetevergarden'
    __official_name__ = 'Violet Evergarden'
    __root_website__ = 'https://zerochan.net/Violet+Evergarden'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

