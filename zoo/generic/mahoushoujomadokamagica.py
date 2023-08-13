from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'mahoushoujomadokamagica'
    __official_name__ = 'Mahou Shoujo Madoka☆Magica'
    __root_website__ = 'https://zerochan.net/Mahou+Shoujo+Madoka%E2%98%86Magica'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

