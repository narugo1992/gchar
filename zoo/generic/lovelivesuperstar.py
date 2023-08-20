from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'lovelivesuperstar'
    __official_name__ = 'Love Live! Superstar!!'
    __root_website__ = 'https://zerochan.net/Love+Live%21+Superstar%21%21'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

