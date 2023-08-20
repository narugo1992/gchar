from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'theidolmster'
    __official_name__ = 'THE iDOLM@STER'
    __root_website__ = 'https://zerochan.net/THE+iDOLM%40STER'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

