import pytest

from gchar.games.nikke import Character


@pytest.mark.unittest
class TestGamesNikkeCharacter:
    def test_character(self, nikke_admi: Character, nikke_neon_blue_ocean: Character, nikke_helm, nikke_quency):
        assert nikke_admi.index == 'admi'
        assert nikke_admi.cnname == '艾德米'
        assert nikke_admi.enname == 'admi'
        assert nikke_admi.jpname == 'アドミ'
        assert nikke_admi.krname == '애드미'
        assert nikke_admi.krnames == ['애드미']
        assert nikke_admi.gender == 'female'
        assert len(nikke_admi.skins) >= 2
        assert nikke_admi.rarity == 3
        assert nikke_admi.clazz == 'supporter'
        assert nikke_admi.burst == 2
        assert nikke_admi.weapon_type == 'sniper rifle'
        assert nikke_admi.manufacturer == 'missilis industry'
        assert nikke_admi.code == 'a.n.m.i. (wind)'
        assert nikke_admi.release_time == pytest.approx(1667520000.0)
        assert not nikke_admi.is_extra
        assert repr(nikke_admi) == '<Character 艾德米/admi/アドミ/애드미, SSR(3***), class: Clazz.SUPPORTER, ' \
                                   'burst: Burst.II, weapon_type: sniper rifle>'

        assert nikke_neon_blue_ocean is not None
        assert nikke_neon_blue_ocean.index == 'neon_blue_ocean'
        assert nikke_neon_blue_ocean.is_extra
        assert repr(nikke_neon_blue_ocean) == \
               '<Character 尼恩：蓝色海洋/neon:_blue_ocean/ネオン：ブルーオーシャン/네온 : 블루 오션, SSR(3***), ' \
               'class: Clazz.ATTACKER, burst: Burst.III, weapon_type: machine gun>'

        assert sorted([nikke_admi, nikke_quency, nikke_helm, nikke_neon_blue_ocean]) == \
               [nikke_neon_blue_ocean, nikke_admi, nikke_helm, nikke_quency]
