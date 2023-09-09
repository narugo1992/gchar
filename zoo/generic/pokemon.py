from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'pokemon'
    __official_name__ = 'Pokémon'
    __root_website__ = 'https://zerochan.net/Pok%C3%A9mon'
    __root_names__ = ['Pokémon', 'GAME FREAK']


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
