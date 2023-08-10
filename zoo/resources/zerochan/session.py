import logging

import requests

from gchar.utils import get_requests_session, srequest

_REF = '/Amiya'


def get_zerochan_session(username: str, password: str, session=None) -> requests.Session:
    session = session or get_requests_session()
    logging.info(f'Logging into zerochan.net with user {username!r} ...')
    resp = srequest(
        session, 'POST', 'https://www.zerochan.net/login',
        data={
            'ref': _REF,
            'name': username,
            'password': password,
            'login': 'Login',
        },
        headers={
            'Referer': 'https://www.zerochan.net/login',
        },
        allow_redirects=False,
    )

    if resp.status_code // 100 == 3:
        logging.info('Login success.')
        assert resp.headers['Location'] == _REF
        return session
    elif resp.status_code // 100 == 2:
        logging.info('Login failed, wrong username or password.')
        raise ValueError('Wrong username or password of zerochan.')
