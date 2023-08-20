from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'loveliveschoolidolfestivalallstars'
    __official_name__ = 'Love Live! School Idol Festival ALL STARS'
    __root_website__ = 'https://zerochan.net/Love+Live%21+School+Idol+Festival+ALL+STARS'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

