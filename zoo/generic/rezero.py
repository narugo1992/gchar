from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'rezero'
    __official_name__ = 'Re:Zero Kara Hajimeru Isekai Seikatsu'
    __root_website__ = 'https://zerochan.net/Re%3AZero+Kara+Hajimeru+Isekai+Seikatsu'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

