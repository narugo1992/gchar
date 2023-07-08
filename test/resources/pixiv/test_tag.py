import pytest

from gchar.resources.pixiv import get_pixiv_keywords


@pytest.mark.unittest
class TestResourcesPixivTag:
    @pytest.mark.parametrize(['ch', 'keyword'], [
        ('lin', 'アークナイツ 林雨霞'),
        ('ling', 'アークナイツ (ling OR リィン OR 令) -cuddling -dressupdarling -lingerie -smilinggirl '
                 '-tickling -令人想摸的肚子 -令人想摸的腿 -博令'),
        ('blazer', 'アークナイツ (blaze OR ブレイズ OR 煌) -博煌 -敦煌 -煌博'),
        ('w', 'w アークナイツ -beeswax -drawing -firewatch -firewhistle -goldenglow -nsfw -schwarz '
              '-shaw -snowsant -steward -swire -waai_fu -wallpaper -warfarin -weed -weedy -whislash '
              '-whisperain -wild_mane -windflit'),
        ('シー', 'アークナイツ (dusk OR シー OR 夕) -ケルシー -シージ -シーメール -シーン '
               '-ドロシー -ルーシー -夕張 -夕日 -夕焼け -夕陽'),
        ('多萝西', 'アークナイツ (dorothy OR ドロシー OR 多萝西)'),
        ('CEO', 'Fate/GrandOrder (berserker_of_el_dorado OR penthesilea OR エルドラドのバーサーカー '
                'OR ペンテシレイア OR 彭忒西勒亚 OR 黄金国的berserker)'),
        ('saber', 'Fate/GrandOrder (altria_pendragon OR アルトリア・ペンドラゴン OR 阿尔托莉雅·潘德拉贡) '
                  '-アルトリア・ペンドラゴン〔オルタ〕 -アルトリア・ペンドラゴン〔サンタオルタ〕 -アルトリア・ペンドラゴン〔リリィ〕 '
                  '-アルトリア・ペンドラゴン・オルタ -アルトリア・ペンドラゴン・リリィ'),
        # ('lee', 'アークナイツ (lee OR 老鲤) -elverleeart -klee -leearknights '
        #         '-leeenfield -lianglee -schleezed -sleep -sleeping -sleepover -sleeveless'),
        ('character_not_found_hahahaha', None)
    ])
    def test_get_pixiv_keywords(self, ch, keyword):
        if keyword is None:
            with pytest.raises(ValueError):
                _ = get_pixiv_keywords(ch)
        else:
            assert get_pixiv_keywords(ch) == keyword

    @pytest.mark.parametrize(['ch', 'keyword', 'warn'], [
        ('lin', 'アークナイツ 林雨霞', True),
        ('ling', 'リィン(アークナイツ)', False),
        ('dusk', 'シー(アークナイツ) -ケルシー -ドロシー', False),
        ('CEO', 'エルドラドのバーサーカー(Fate) ペンテシレイア(Fate)', False),
    ])
    def test_get_pixiv_keywords_simple(self, ch, keyword, warn):
        with pytest.warns(UserWarning if warn else None):
            assert get_pixiv_keywords(ch, simple=True) == keyword
