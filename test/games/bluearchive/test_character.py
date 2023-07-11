import pytest

from gchar.games.bluearchive import Character


@pytest.mark.unittest
class TestGamesBluearchive:
    def test_character(self, ba_toki: Character, ba_yuuka: Character):
        assert ba_toki.index == 'toki'
        assert ba_toki.cnname == '时'
        assert ba_toki.jpname == '飛鳥馬トキ'
        assert ba_toki.enname == 'toki'
        assert ba_toki.gender == 'female'
        assert ba_toki.rarity == 3
        assert ba_toki.role == 'ATTACKER'
        assert ba_toki.weapon_type == 'AR'
        assert ba_toki.attack_type == 'EXPLOSIVE'
        assert len(ba_toki.skins) >= 2
        assert ba_toki.release_time == pytest.approx(1677056400.0)
        assert repr(ba_toki) == '<Character 时/季/toki/asuma_toki/飛鳥馬トキ, SSR(3***), role: Role.ATTACKER, ' \
                                'attack: AttackType.EXPLOSIVE, weapon: WeaponType.AR>'

        assert ba_yuuka.index == 'yuuka'
        assert ba_yuuka.cnname == '优香'
        assert ba_yuuka.jpname == '早瀬ユウカ'
        assert ba_yuuka.enname == 'yuuka'
        assert ba_yuuka.gender == 'female'
        assert ba_yuuka.rarity == 2
        assert ba_yuuka.role == 'TANK'
        assert ba_yuuka.weapon_type == 'SMG'
        assert ba_yuuka.attack_type == 'EXPLOSIVE'
        assert len(ba_yuuka.skins) >= 2
        assert ba_yuuka.release_time == pytest.approx(1612429200.0)
        assert repr(ba_yuuka) == '<Character 优香/yuuka/hayase_yuuka/早瀬ユウカ/早濑ユウカ, SR(2**), role: Role.TANK, ' \
                                 'attack: AttackType.EXPLOSIVE, weapon: WeaponType.SMG>'

        assert ba_yuuka < ba_toki
