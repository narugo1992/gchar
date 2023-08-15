from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'kantaicollection'
    __official_name__ = 'Kantai Collection'
    __root_website__ = 'https://zerochan.net/Kantai+Collection'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

