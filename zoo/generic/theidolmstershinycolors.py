from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'theidolmstershinycolors'
    __official_name__ = 'THE iDOLM@STER: SHINY COLORS'
    __root_website__ = 'https://zerochan.net/THE+iDOLM%40STER%3A+SHINY+COLORS'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

