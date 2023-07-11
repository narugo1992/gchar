import pytest

from gchar.games.bluearchive import Rarity, WeaponType, Role, AttackType


@pytest.mark.unittest
class TestGamesBluearchive:
    def test_rarity(self):
        assert Rarity.R == 0x1
        assert Rarity.loads(0x1) == Rarity.R
        assert Rarity.loads(Rarity.R) == Rarity.R
        assert Rarity.SR == 0x2
        assert Rarity.loads(0x2) == Rarity.SR
        assert Rarity.loads(Rarity.SR) == Rarity.SR
        assert Rarity.SSR == 0x3
        assert Rarity.loads(0x3) == Rarity.SSR
        assert Rarity.loads(Rarity.SSR) == Rarity.SSR

        with pytest.raises(ValueError):
            _ = Rarity.loads(0x100)
        with pytest.raises(TypeError):
            _ = Rarity.loads('lk;dfjk')

    def test_weapon_type(self):
        assert WeaponType.SMG == 'SMG'
        assert WeaponType.loads('SMG') == WeaponType.SMG
        assert WeaponType.loads(WeaponType.SMG) == WeaponType.SMG
        assert WeaponType.RL == 'RL'
        assert WeaponType.loads('RL') == WeaponType.RL
        assert WeaponType.loads(WeaponType.RL) == WeaponType.RL
        assert WeaponType.HG == 'HG'
        assert WeaponType.loads('HG') == WeaponType.HG
        assert WeaponType.loads(WeaponType.HG) == WeaponType.HG
        assert WeaponType.FT == 'FT'
        assert WeaponType.loads('FT') == WeaponType.FT
        assert WeaponType.loads(WeaponType.FT) == WeaponType.FT
        assert WeaponType.SG == 'SG'
        assert WeaponType.loads('SG') == WeaponType.SG
        assert WeaponType.loads(WeaponType.SG) == WeaponType.SG
        assert WeaponType.MT == 'MT'
        assert WeaponType.loads('MT') == WeaponType.MT
        assert WeaponType.loads(WeaponType.MT) == WeaponType.MT
        assert WeaponType.AR == 'AR'
        assert WeaponType.loads('AR') == WeaponType.AR
        assert WeaponType.loads(WeaponType.AR) == WeaponType.AR
        assert WeaponType.MG == 'MG'
        assert WeaponType.loads('MG') == WeaponType.MG
        assert WeaponType.loads(WeaponType.MG) == WeaponType.MG
        assert WeaponType.GL == 'GL'
        assert WeaponType.loads('GL') == WeaponType.GL
        assert WeaponType.loads(WeaponType.GL) == WeaponType.GL
        assert WeaponType.SR == 'SR'
        assert WeaponType.loads('SR') == WeaponType.SR
        assert WeaponType.loads(WeaponType.SR) == WeaponType.SR
        assert WeaponType.RG == 'RG'
        assert WeaponType.loads('RG') == WeaponType.RG
        assert WeaponType.loads(WeaponType.RG) == WeaponType.RG

        assert WeaponType.RG != None
        with pytest.raises(ValueError):
            _ = WeaponType.loads('s;dlfjlsdf')
        with pytest.raises(TypeError):
            _ = WeaponType.loads([1, 2, 3])

    def test_role(self):
        assert Role.ATTACKER == 'ATTACKER'
        assert Role.loads('ATTACKER') == Role.ATTACKER
        assert Role.loads(Role.ATTACKER) == Role.ATTACKER
        assert Role.TACTICAL_SUPPORT == 'TACTICAL SUPPORT'
        assert Role.loads('TACTICAL SUPPORT') == Role.TACTICAL_SUPPORT
        assert Role.loads(Role.TACTICAL_SUPPORT) == Role.TACTICAL_SUPPORT
        assert Role.HEALER == 'HEALER'
        assert Role.loads('HEALER') == Role.HEALER
        assert Role.loads(Role.HEALER) == Role.HEALER
        assert Role.SUPPORT == 'SUPPORT'
        assert Role.loads('SUPPORT') == Role.SUPPORT
        assert Role.loads(Role.SUPPORT) == Role.SUPPORT
        assert Role.TANK == 'TANK'
        assert Role.loads('TANK') == Role.TANK
        assert Role.loads(Role.TANK) == Role.TANK

        assert Role.TANK != None
        with pytest.raises(ValueError):
            _ = Role.loads('sdklfjlsdf')
        with pytest.raises(TypeError):
            _ = Role.loads([1, 2, 3])

    def test_attack_type(self):
        assert AttackType.PENETRATION == 'PENETRATION'
        assert AttackType.loads('PENETRATION') == AttackType.PENETRATION
        assert AttackType.loads(AttackType.PENETRATION) == AttackType.PENETRATION
        assert AttackType.EXPLOSIVE == 'EXPLOSIVE'
        assert AttackType.loads('EXPLOSIVE') == AttackType.EXPLOSIVE
        assert AttackType.loads(AttackType.EXPLOSIVE) == AttackType.EXPLOSIVE
        assert AttackType.MYSTIC == 'MYSTIC'
        assert AttackType.loads('MYSTIC') == AttackType.MYSTIC
        assert AttackType.loads(AttackType.MYSTIC) == AttackType.MYSTIC

        assert AttackType.MYSTIC != None
        with pytest.raises(ValueError):
            _ = AttackType.loads(';ldfk;dls')
        with pytest.raises(TypeError):
            _ = AttackType.loads([1, 2, 3])
