from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'bangdreamdai2ki'
    __official_name__ = 'BanG Dream! Dai 2-ki'
    __root_website__ = 'https://zerochan.net/BanG+Dream%21+Dai+2-ki'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

