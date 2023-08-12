from ._base import ZerochanBasedIndexer


class NARUTOIndexer(ZerochanBasedIndexer):
    __game_name__ = 'naruto'
    __official_name__ = 'NARUTO'
    __root_website__ = 'https://zerochan.net/NARUTO'


INDEXER = NARUTOIndexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
