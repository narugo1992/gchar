from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'isitwrongtotrytopickupgirlsinadungeon'
    __official_name__ = 'Dungeon ni Deai wo Motomeru no wa Machigatteiru no Darou ka'
    __root_website__ = 'https://zerochan.net/Dungeon+ni+Deai+wo+Motomeru+no+wa+Machigatteiru+no+Darou+ka'


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()

