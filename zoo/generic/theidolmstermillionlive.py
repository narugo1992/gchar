from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'theidolmstermillionlive'
    __official_name__ = 'THE iDOLM@STER: Million Live!'
    __root_website__ = 'https://zerochan.net/THE+iDOLM%40STER%3A+Million+Live%21'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

