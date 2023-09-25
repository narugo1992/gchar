from ._base import ZerochanBasedIndexer


class Indexer(ZerochanBasedIndexer):
    __game_name__ = 'bangdream'
    __official_name__ = 'BanG Dream!'
    __root_website__ = 'https://zerochan.net/BanG+Dream%21'
    __root_names__ = [
        "BanG Dream! Girls Band Party!",
        "BanG Dream!",
        "BanG Dream! Dai 2-ki",
        "BanG Dream! Girls Band Party! PICO",
        "BanG Dream! 3rd Season",
        "Bang Dream! Girls Band Party! PICO ~OHMORI~",
        "BanG Dream! Episode of Roselia I: Yakusoku",
        "Bang Dream! Girls Band Party! PICO: Fever!",
        "BanG Dream! Episode of Roselia II: Song I am",
        "BanG Dream! FILM LIVE 2nd Stage",
        "Bang Dream! FILM LIVE",
        "BanG Dream! Poppin Dream!",
        "BanG Dream! 11th☆LIVE",
        "BanG Dream! Special☆LIVE Girls Band Party! 2020",
        "BanG Dream! Special☆LIVE Girls Band Party! 2020→2022",
        "Bang Dream! 2nd Illustration Contest"
    ]


INDEXER = Indexer()

if __name__ == '__main__':
    INDEXER.get_cli()()
