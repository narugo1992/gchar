from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'honkai3'
    __official_name__ = 'Houkai 3rd'
    __root_website__ = 'https://zerochan.net/Houkai+3rd'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

