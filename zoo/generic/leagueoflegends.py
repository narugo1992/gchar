from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'leagueoflegends'
    __official_name__ = 'League of Legends'
    __root_website__ = 'https://zerochan.net/League+of+Legends'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

