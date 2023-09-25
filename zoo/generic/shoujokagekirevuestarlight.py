from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'shoujokagekirevuestarlight'
    __official_name__ = 'Shoujo☆Kageki Revue Starlight'
    __root_website__ = 'https://zerochan.net/Shoujo%E2%98%86Kageki+Revue+Starlight'
    __root_names__ = [
        "Shoujo☆Kageki Revue Starlight -ReLIVE-",
        "Shoujo☆Kageki Revue Starlight",
        "Gekijouban Shoujo☆Kageki Revue Starlight",
        "Shoujo☆Kageki Revue Starlight: Rondo Rondo Rondo"
    ]


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
