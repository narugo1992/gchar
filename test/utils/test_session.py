import pytest
from requests import RequestException

from gchar.utils import get_requests_session, srequest


@pytest.fixture(scope='module')
def session():
    yield get_requests_session()


@pytest.fixture(scope='module')
def nian_skin_etag():
    return '"7f9608c447fd74878ec33714d2a81e0c"'


@pytest.mark.unittest
class TestUtilsSession:
    def test_srequest(self, url_to_game_character_skins, session, nian_skin_etag, url_to_testfile):
        resp = srequest(session, 'HEAD', f'{url_to_game_character_skins}/arknights/NM01/乐逍遥.png')
        assert resp.status_code == 200
        assert resp.headers.get('etag') == nian_skin_etag

        resp = srequest(
            session, 'HEAD', f'{url_to_game_character_skins}/arknights/NM01/乐逍遥.png',
            headers={'If-None-Match': nian_skin_etag},
        )
        assert resp.status_code == 304

        with pytest.raises(RequestException):
            _ = srequest(session, 'HEAD', f'{url_to_testfile}/_file_should_not_exist')

        resp = srequest(session, 'HEAD', f'{url_to_testfile}/_file_should_not_exist', raise_for_status=False)
        assert resp.status_code == 404
