from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'lovelive'
    __official_name__ = 'Love Live!'
    __root_website__ = 'https://zerochan.net/Love+Live%21'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

