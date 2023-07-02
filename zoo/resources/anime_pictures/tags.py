from tqdm.auto import tqdm

from gchar.utils import get_requests_session, srequest

get_requests_session()


def crawl_tags_to_json():
    session = get_requests_session()
    offset = 0
    retval = []
    pg = tqdm(desc='Tag Crawl')
    while True:
        resp = srequest(session, 'GET', 'https://anime-pictures.net/api/v3/tags?offset=131000&limit=1000&lang=en',
                        params={
                            'lang': 'en',
                            'offset': str(offset),
                            'limit': '100',
                        })
        resp.raise_for_status()

        tags = resp.json()['tags']
        if not tags:
            break

        retval.extend(tags)
        offset += len(tags)
        if offset >= 200:
            break
        pg.update()

    pg.close()
    return retval
