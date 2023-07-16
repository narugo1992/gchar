import pandas as pd
from hbutils.string import plural_word
from hbutils.system import urlsplit

from gchar.resources.sites import list_available_sites
from gchar.resources.sites.base import SITES

if __name__ == '__main__':
    print(f'In addition to that, we also support {plural_word(len(SITES), "popular image website")} and '
          f'can retrieve recommended search terms for known characters on these websites using '
          f'the :func:`gchar.resources.sites.get_site_tag` function. '
          f'The following are the currently supported websites:')
    print()

    columns = ['Site', 'Website']
    data = []
    for site in list_available_sites():
        url = f'https://{SITES[site]}'
        host = urlsplit(url).host
        short_host = '.'.join(host.split('.')[-2:])
        data.append((site, f'`{short_host} <{url}>`_'))

    df = pd.DataFrame(columns=columns, data=data)
    print(df.to_markdown(headers='keys', tablefmt='rst', index=False))
