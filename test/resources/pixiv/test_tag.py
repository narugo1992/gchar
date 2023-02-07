import pytest

from gchar.resources.pixiv import get_pixiv_keywords


@pytest.mark.unittest
class TestResourcesPixivTag:
    @pytest.mark.parametrize(['ch', 'keyword'], [
        ('lin', 'アークナイツ (lin OR 林) -angelina -flint -folinic -ling -守林人 -巡林者 -杜林'),
        ('ling', 'アークナイツ (ling OR リィン OR 令)'),
        ('blazer', 'アークナイツ (blaze OR ブレイズ OR 煌)'),
        ('w', 'w アークナイツ -beeswax -firewatch -firewhistle -goldenglow -schwarz -shaw '
              '-snowsant -steward -swire -waai_fu -warfarin -weedy -whislash -whisperain '
              '-wild_mane -windflit'),
        ('シー', 'アークナイツ (dusk OR シー OR 夕) -ケルシー -シージ -シーン'),
        ('多萝西', 'アークナイツ (dorothy OR 多萝西)'),
        ('aak', 'アークナイツ (aak OR 阿) -阿消 -阿米娅'),
        ('CEO', 'Fate/GrandOrder (berserker_of_el_dorado OR penthesilea OR エルドラドのバーサーカー '
                'OR ペンテシレイア OR 彭忒西勒亚 OR 黄金国的berserker)'),
        ('saber', 'Fate/GrandOrder (altria_pendragon OR アルトリア・ペンドラゴン OR 阿尔托莉雅·潘德拉贡) '
                  '-アルトリア・ペンドラゴン〔オルタ〕 -アルトリア・ペンドラゴン〔サンタオルタ〕 -アルトリア・ペンドラゴン〔リリィ〕'),
        ('character_not_found_hahahaha', None)
    ])
    def test_get_pixiv_keywords(self, ch, keyword):
        if keyword is None:
            with pytest.raises(ValueError):
                _ = get_pixiv_keywords(ch)
        else:
            assert get_pixiv_keywords(ch, ) == keyword

    @pytest.mark.parametrize(['ch', 'keyword', 'warn'], [
        ('lin', 'アークナイツ (lin OR 林) -angelina -flint -folinic -ling -守林人 -巡林者 -杜林', True),
        ('ling', 'リィン(アークナイツ)', False),
        ('dusk', 'シー(アークナイツ) -ケルシー', False),
        ('CEO', 'エルドラドのバーサーカー(Fate) ペンテシレイア(Fate)', False),
    ])
    def test_get_pixiv_keywords_simple(self, ch, keyword, warn):
        with pytest.warns(UserWarning if warn else None):
            assert get_pixiv_keywords(ch, simple=True) == keyword
