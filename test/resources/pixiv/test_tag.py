import pytest

from gchar.resources.pixiv import get_pixiv_keywords


@pytest.mark.unittest
class TestResourcesPixivTag:
    @pytest.mark.parametrize(['ch', 'keyword'], [
        ('lin', 'アークナイツ 林雨霞'),
        ('ling', 'アークナイツ (ling OR リィン OR 令) -lingerie -pearling -smiling -tickling '
                 '-wrestling -xiangling -博令 -生類憐れみの令'),
        ('blazer', 'アークナイツ (blaze OR ブレイズ OR 煌) -博煌 -煌喉'),
        ('w', 'w アークナイツ -beeswax -bsw -firewatch -firewhistle -flowey -goldenglow -schwarz -shaw -snowsant '
              '-steward -swimsuit -swire -waai_fu -warfarin -weedy -whislash -whisperain -wild_mane -windflit -wフェラ'),
        ('シー', 'アークナイツ (dusk OR シー OR 夕) -ケルシー -シージ -シースルー -シートベルト -シーン '
               '-セクシー -センターシーム -ドロシー -七夕 -博夕 -夕暮れ -明日方舟夕'),
        ('多萝西', 'アークナイツ (dorothy OR 多萝西)'),
        ('aak', 'アークナイツ (aak OR 阿) -博阿 -阿丝忒菈 -阿丽娜 -阿咬 -阿方索 -阿波尼亚 -阿消 -阿米亚 '
                '-阿米娅 -阿米婭 -阿米驴 -阿芙茉妮 -阿赫茉妮 -阿陈 -阿黑颜'),
        ('CEO', 'Fate/GrandOrder (berserker_of_el_dorado OR penthesilea OR エルドラドのバーサーカー '
                'OR ペンテシレイア OR 彭忒西勒亚 OR 黄金国的berserker)'),
        ('saber', 'Fate/GrandOrder (altria_pendragon OR アルトリア・ペンドラゴン OR 阿尔托莉雅·潘德拉贡) '
                  '-アルトリア・ペンドラゴン〔オルタ〕 -アルトリア・ペンドラゴン〔サンタオルタ〕 -アルトリア・ペンドラゴン〔リリィ〕 '
                  '-アルトリア・ペンドラゴン・オルタ -アルトリア・ペンドラゴン・リリィ'),
        ('lee', 'アークナイツ (lee OR 老鲤) -elverleeart -klee -leearknights '
                '-leeenfield -lianglee -schleezed -sleep -sleeping -sleepover -sleeveless'),
        ('character_not_found_hahahaha', None)
    ])
    def test_get_pixiv_keywords(self, ch, keyword):
        if keyword is None:
            with pytest.raises(ValueError):
                _ = get_pixiv_keywords(ch)
        else:
            assert get_pixiv_keywords(ch, ) == keyword

    @pytest.mark.parametrize(['ch', 'keyword', 'warn'], [
        ('lin', 'アークナイツ 林雨霞', True),
        ('ling', 'リィン(アークナイツ)', False),
        ('dusk', 'シー(アークナイツ) -ケルシー', False),
        ('CEO', 'エルドラドのバーサーカー(Fate) ペンテシレイア(Fate)', False),
    ])
    def test_get_pixiv_keywords_simple(self, ch, keyword, warn):
        with pytest.warns(UserWarning if warn else None):
            assert get_pixiv_keywords(ch, simple=True) == keyword
