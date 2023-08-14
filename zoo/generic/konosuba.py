from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'konosuba'
    __official_name__ = 'Kono Subarashii Sekai ni Shukufuku wo!'
    __root_website__ = 'https://zerochan.net/Kono+Subarashii+Sekai+ni+Shukufuku+wo%21'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

