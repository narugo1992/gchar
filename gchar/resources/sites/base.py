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
    'wallhaven': 'wallhaven.cc',
}


def list_available_sites() -> List[str]:
    """
    List the available supported image website names.

    :return: The list of supported website names.
    :rtype: List[str]

    Examples::
        >>> from gchar.resources.sites import list_available_sites
        >>>
        >>> list_available_sites()
        ['anime_pictures', 'atfbooru', 'danbooru', 'hypnohub', 'konachan', 'konachan_net', 'lolibooru', 'rule34', 'safebooru', 'sankaku', 'xbooru', 'yande', 'zerochan']
    """
    return sorted(SITES.keys())
