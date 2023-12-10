import pytest

from gchar.games.azurlane import Character, Group


@pytest.mark.unittest
class TestGamesAzurlaneCharacter:
    def test_basic(self, azl_new_jersey: Character, azl_maury: Character, azl_fuso_meta: Character,
                   azl_san_diego_refit: Character, azl_gascogne_mu: Character, azl_hiei_chan: Character,
                   azl_u556: Character, azl_azuma: Character):
        assert azl_new_jersey == '068'
        assert azl_new_jersey == '新泽西'
        assert azl_new_jersey.cnname == '新泽西'
        assert azl_new_jersey == 'new_jersey'
        assert azl_new_jersey.enname == 'new_jersey'
        assert azl_new_jersey == 'ニュージャージー'
        assert azl_new_jersey.jpname == 'ニュージャージー'
        assert azl_new_jersey.gender == 'female'
        assert azl_new_jersey.rarity == 5
        assert azl_new_jersey.group == Group.USS
        assert not azl_new_jersey.is_meta
        assert not azl_new_jersey.is_refit
        assert not azl_new_jersey.is_mu
        assert not azl_new_jersey.is_chibi
        assert not azl_new_jersey.is_extra
        assert repr(azl_new_jersey) == '<Character 068 - 新泽西/new_jersey/ニュージャージー, ' \
                                       '海上传奇(5*****), group: Group.USS>'
        assert azl_new_jersey.release_time == pytest.approx(1622106000.0)
        assert len(azl_new_jersey.skins) >= 7

        assert azl_maury == '010'
        assert azl_maury == '莫里'
        assert azl_maury.cnname == '莫里'
        assert azl_maury == 'maury'
        assert azl_maury.enname == 'maury'
        assert azl_maury == 'モーリー'
        assert azl_maury.jpname == 'モーリー'
        assert azl_maury.rarity == 3
        assert azl_maury.group == Group.USS
        assert azl_maury.gender == 'female'
        assert not azl_maury.is_meta
        assert not azl_maury.is_refit
        assert not azl_maury.is_mu
        assert not azl_maury.is_chibi
        assert not azl_maury.is_extra
        assert repr(azl_maury) == '<Character 010 - 莫里/maury/モーリー, 精锐(3***), group: Group.USS>'
        assert azl_maury.release_time == pytest.approx(1495702800.0)

        assert azl_fuso_meta == 'META005'
        assert azl_fuso_meta == '扶桑·meta'
        assert azl_fuso_meta.cnname == '扶桑·meta'
        assert azl_fuso_meta == 'fuso_meta'
        assert azl_fuso_meta.enname == 'fuso_meta'
        assert azl_fuso_meta == '扶桑(meta)'
        assert azl_fuso_meta.jpname == '扶桑(meta)'
        assert azl_fuso_meta.rarity == 3
        assert azl_fuso_meta.group == 'META-???'
        assert azl_fuso_meta.is_meta
        assert azl_fuso_meta.gender == 'female'
        assert not azl_fuso_meta.is_refit
        assert not azl_fuso_meta.is_mu
        assert not azl_fuso_meta.is_chibi
        assert azl_fuso_meta.is_extra
        assert repr(azl_fuso_meta) == '<Character META005 - 扶桑·META/fuso_meta/扶桑(META), 精锐(3***), group: META-???>'

        assert azl_san_diego_refit == '036'
        assert azl_san_diego_refit == '圣地亚哥.改'
        assert azl_san_diego_refit.cnname == '圣地亚哥.改'
        assert azl_san_diego_refit == 'san_diego'
        assert azl_san_diego_refit.enname == 'san_diego'
        assert azl_san_diego_refit == 'サンディエゴ'
        assert azl_san_diego_refit.jpname == 'サンディエゴ'
        assert azl_san_diego_refit.rarity == 5
        assert azl_san_diego_refit.group == Group.USS
        assert not azl_san_diego_refit.is_meta
        assert azl_san_diego_refit.is_refit
        assert not azl_san_diego_refit.is_mu
        assert not azl_san_diego_refit.is_chibi
        assert azl_san_diego_refit.is_extra
        assert repr(azl_san_diego_refit) == '<Character 036 - 圣地亚哥.改/san_diego/サンディエゴ, ' \
                                            '海上传奇(5*****), group: Group.USS>'

        assert azl_gascogne_mu == '418'
        assert azl_gascogne_mu == '加斯科涅(μ兵装)'
        assert azl_gascogne_mu.cnname == '加斯科涅(μ兵装)'
        assert azl_gascogne_mu == 'gascogne'
        assert azl_gascogne_mu.enname == 'gascogne'
        assert azl_gascogne_mu == 'ガスコーニュ（μ兵装）'
        assert azl_gascogne_mu.jpname == 'ガスコーニュ（μ兵装）'
        assert azl_gascogne_mu.rarity == 4
        assert azl_gascogne_mu.group == Group.MNF
        assert not azl_gascogne_mu.is_meta
        assert not azl_gascogne_mu.is_refit
        assert azl_gascogne_mu.is_mu
        assert not azl_gascogne_mu.is_chibi
        assert azl_gascogne_mu.is_extra
        assert repr(azl_gascogne_mu) == '<Character 418 - 加斯科涅(μ兵装)/gascogne/ガスコーニュ（μ兵装）, ' \
                                        '超稀有(4****), group: Group.MNF>'

        assert azl_hiei_chan == '383'
        assert azl_hiei_chan == '小比叡'
        assert azl_hiei_chan.cnname == '小比叡'
        assert azl_hiei_chan == 'hiei_chan'
        assert azl_hiei_chan.enname == 'hiei_chan'
        assert azl_hiei_chan == '比叡ちゃん'
        assert azl_hiei_chan.jpname == '比叡ちゃん'
        assert azl_hiei_chan.rarity == 3
        assert azl_hiei_chan.group == Group.IJN
        assert not azl_hiei_chan.is_meta
        assert not azl_hiei_chan.is_refit
        assert not azl_hiei_chan.is_mu
        assert azl_hiei_chan.is_chibi
        assert azl_hiei_chan.is_extra
        assert repr(azl_hiei_chan) == '<Character 383 - 小比叡/hiei_chan/比叡ちゃん, ' \
                                      '精锐(3***), group: Group.IJN>'

        assert azl_u556 == '386'
        assert azl_u556 == 'u-556'
        assert azl_u556.cnname == 'u-556'
        assert azl_u556 == 'u_556'
        assert azl_u556.enname == 'u_556'
        assert azl_u556.jpname is None
        assert azl_u556.jpnames == []
        assert azl_u556.rarity == 3
        assert azl_u556.group == Group.KMS
        assert not azl_u556.is_meta
        assert not azl_u556.is_refit
        assert not azl_u556.is_mu
        assert not azl_u556.is_chibi
        assert not azl_u556.is_extra
        assert repr(azl_u556) == '<Character 386 - U-556/u_556, 精锐(3***), group: Group.KMS>'

        assert azl_azuma == 'Plan010'
        assert azl_azuma == '吾妻'
        assert azl_azuma.cnname == '吾妻'
        assert azl_azuma == 'azuma'
        assert azl_azuma.enname == 'azuma'
        assert azl_azuma == '吾妻'
        assert azl_azuma == 'あづま'
        assert azl_azuma.jpname == '吾妻'
        assert azl_azuma.jpnames == ['吾妻', 'あづま']
        assert azl_azuma.rarity == 5
        assert azl_azuma.group == Group.IJN
        assert not azl_azuma.is_meta
        assert not azl_azuma.is_refit
        assert not azl_azuma.is_mu
        assert not azl_azuma.is_chibi
        assert not azl_azuma.is_extra
        assert repr(azl_azuma) == '<Character Plan010 - 吾妻/azuma/吾妻/あづま, 决战方案(5*****), group: Group.IJN>'

        assert sorted([azl_new_jersey, azl_maury, azl_azuma, azl_san_diego_refit]) == \
               [azl_maury, azl_san_diego_refit, azl_azuma, azl_new_jersey]
