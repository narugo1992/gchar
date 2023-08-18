from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'warshipgirls'
    __official_name__ = 'Zhan Jian Shao Nyu'
    __root_website__ = 'https://zerochan.net/Zhan+Jian+Shao+Nyu'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

