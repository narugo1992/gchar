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
    ])
    def test_get_pixiv_keywords(self, ch, keyword):
        assert get_pixiv_keywords(ch, ) == keyword

    @pytest.mark.parametrize(['ch', 'keyword'], [
        ('lin', None),
        ('ling', 'リィン(アークナイツ)'),
        ('dusk', 'シー(アークナイツ) -ケルシー'),
        ('CEO', 'ペンテシレイア(Fate)'),
    ])
    def test_get_pixiv_keywords_simple(self, ch, keyword):
        if keyword:
            assert get_pixiv_keywords(ch, simple=True) == keyword
        else:
            with pytest.raises(ValueError):
                _ = get_pixiv_keywords(ch, simple=True)
