from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'granbluefantasy'
    __official_name__ = 'Granblue Fantasy'
    __root_website__ = 'https://zerochan.net/Granblue+Fantasy'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

