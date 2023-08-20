from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'idolmastercinderellagirls'
    __official_name__ = 'THE iDOLM@STER: Cinderella Girls'
    __root_website__ = 'https://zerochan.net/THE+iDOLM%40STER%3A+Cinderella+Girls'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

