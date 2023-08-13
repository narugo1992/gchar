from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'yugioh'
    __official_name__ = 'Yu-Gi-Oh!'
    __root_website__ = 'https://zerochan.net/Yu-Gi-Oh%21'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

