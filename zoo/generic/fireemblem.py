from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'fireemblem'
    __official_name__ = 'Fire Emblem'
    __root_website__ = 'https://zerochan.net/Fire+Emblem+Series?q=Fire+Emblem+Series'
    __root_names__ = [
        "Fire Emblem Series", "Fire Emblem Heroes", "Fire Emblem: Kakusei", "Fire Emblem If",
        "Fire Emblem: Fuuka Setsugetsu", "Fire Emblem Gaiden", "TCG Fire Emblem 0", "Fire Emblem Engage",
        "Fire Emblem Musou",
    ]


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
