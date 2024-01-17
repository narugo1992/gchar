from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'eiyuudensetsusennokiseki'
    __official_name__ = 'Eiyuu Densetsu: Sen no Kiseki'
    __root_website__ = 'https://zerochan.net/Eiyuu+Densetsu%3A+Sen+no+Kiseki'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

