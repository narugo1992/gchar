from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'swordartonline'
    __official_name__ = 'Sword Art Online'
    __root_website__ = 'https://zerochan.net/Sword+Art+Online'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

