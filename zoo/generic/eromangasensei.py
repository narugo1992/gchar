from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'eromangasensei'
    __official_name__ = 'Eromanga Sensei'
    __root_website__ = 'https://zerochan.net/Eromanga+Sensei'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

