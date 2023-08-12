from typing import List

import pytest

from gchar.resources.pixiv import get_pixiv_keywords


@pytest.mark.unittest
class TestResourcesPixivTag:
    @pytest.mark.parametrize(['ch', 'keyword', 'forbidden_words'], [
        # ('lin', 'アークナイツ 林雨霞', []),
        ('ling', 'アークナイツ (ling OR リィン OR 令)', []),
        ('blazer', 'アークナイツ (blaze OR ブレイズ OR 煌)', []),
        ('w', 'w アークナイツ', ['schwarz', 'warfarin']),
        ('シー', 'アークナイツ (dusk OR シー OR 夕)', ['ケルシー', 'ドロシー']),
        ('多萝西', 'アークナイツ (dorothy OR ドロシー OR 多萝西)', []),
        ('CEO', 'Fate/GrandOrder (berserker_of_el_dorado OR penthesilea OR エルドラドのバーサーカー '
                'OR ペンテシレイア OR 彭忒西勒亚 OR 黄金国的berserker)', []),
        ('saber', 'Fate/GrandOrder (altria_pendragon OR アルトリア・ペンドラゴン OR 阿尔托莉雅·潘德拉贡)', []),
        ('character_not_found_hahahaha' * 20, None, [])
    ])
    def test_get_pixiv_keywords(self, ch, keyword: str, forbidden_words: List[str]):
        if keyword is None:
            with pytest.raises(ValueError):
                _ = get_pixiv_keywords(ch)
        else:
            actual_keyword = get_pixiv_keywords(ch)
            assert keyword in actual_keyword, \
                f'Expected keyword {keyword!r} not found in actual keyword - {actual_keyword!r}.'

            for forbid_word in forbidden_words:
                assert f'-{forbid_word}' in actual_keyword, \
                    f'Expected forbidden word {forbid_word!r} not found in actual keyword - {actual_keyword!r}.'

    @pytest.mark.parametrize(['ch', 'keyword', 'warn'], [
        # ('lin', 'アークナイツ 林雨霞', True),
        ('ling', 'リィン(アークナイツ)', False),
        ('dusk', 'シー(アークナイツ) -ケルシー -ドロシー', False),
        ('CEO', 'エルドラドのバーサーカー(Fate) ペンテシレイア(Fate)', False),
    ])
    def test_get_pixiv_keywords_simple(self, ch, keyword, warn):
        with pytest.warns(UserWarning if warn else None):
            assert get_pixiv_keywords(ch, simple=True) == keyword
