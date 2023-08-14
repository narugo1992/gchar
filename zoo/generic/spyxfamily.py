from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'spyxfamily'
    __official_name__ = 'Spy × Family'
    __root_website__ = 'https://zerochan.net/Spy+%C3%97+Family'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

