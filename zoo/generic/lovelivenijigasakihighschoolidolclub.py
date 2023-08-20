from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'lovelivenijigasakihighschoolidolclub'
    __official_name__ = 'Love Live! Nijigasaki Gakuen School Idol Doukoukai'
    __root_website__ = 'https://zerochan.net/Love+Live%21+Nijigasaki+Gakuen+School+Idol+Doukoukai'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

