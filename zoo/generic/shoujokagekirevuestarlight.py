from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'shoujokagekirevuestarlight'
    __official_name__ = 'Shoujo☆Kageki Revue Starlight'
    __root_website__ = 'https://zerochan.net/Shoujo%E2%98%86Kageki+Revue+Starlight'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

