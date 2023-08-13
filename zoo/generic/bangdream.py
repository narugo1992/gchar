from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'bangdream'
    __official_name__ = 'BanG Dream!'
    __root_website__ = 'https://zerochan.net/BanG+Dream%21'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

