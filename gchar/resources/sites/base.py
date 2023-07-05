from typing import List

SITES = {
    'anime_pictures': 'anime-pictures.net',
    'atfbooru': 'booru.allthefallen.moe',
    'sankaku': 'chan.sankakucomplex.com',
    'danbooru': 'danbooru.donmai.us',
    'hypnohub': 'hypnohub.net',
    'konachan': 'konachan.com',
    'konachan_net': 'konachan.net',
    'lolibooru': 'lolibooru.moe',
    'rule34': 'rule34.xxx',
    'safebooru': 'safebooru.donmai.us',
    'xbooru': 'xbooru.com',
    'yande': 'yande.re',
    'zerochan': 'zerochan.net',
}


def list_available_sites() -> List[str]:
    return sorted(SITES.keys())
