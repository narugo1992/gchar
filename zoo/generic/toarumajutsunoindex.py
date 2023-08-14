from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'toarumajutsunoindex'
    __official_name__ = 'To Aru Majutsu no Index'
    __root_website__ = 'https://zerochan.net/To+Aru+Majutsu+no+Index'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

