import pytest

from gchar.games.azurlane import Group, BasicRarity, ResearchRarity


@pytest.mark.unittest
class TestGamesAzurlaneProperty:
    def test_group(self):
        assert Group.loads('白鹰') == Group.USS
        assert Group.loads(Group.USS) == '白鹰'
        assert Group.loads('皇家') == Group.HMS
        assert Group.loads(Group.HMS) == '皇家'
        assert Group.loads('重樱') == Group.IJN
        assert Group.loads(Group.IJN) == '重樱'
        assert Group.loads('铁血') == Group.KMS
        assert Group.loads(Group.KMS) == '铁血'
        assert Group.loads('东煌') == Group.DE
        assert Group.loads(Group.DE) == '东煌'
        assert Group.loads('撒丁帝国') == Group.RN
        assert Group.loads(Group.RN) == '撒丁帝国'
        assert Group.loads('北方联合') == Group.SN
        assert Group.loads(Group.SN) == '北方联合'
        assert Group.loads('自由鸢尾') == Group.FFNF
        assert Group.loads(Group.FFNF) == '自由鸢尾'
        assert Group.loads('维希教廷') == Group.MNF
        assert Group.loads(Group.MNF) == '维希教廷'
        assert Group.MNF != 'xxx'
        assert Group.MNF != None
        with pytest.raises(ValueError):
            _ = Group.loads('xxx')
        with pytest.raises(TypeError):
            _ = Group.loads(None)

    def test_basic_rarity(self):
        assert BasicRarity.loads('普通') == BasicRarity.COMMON
        assert BasicRarity.loads(1) == BasicRarity.COMMON
        assert BasicRarity.loads(BasicRarity.COMMON) == '普通'
        assert BasicRarity.COMMON == 1
        assert BasicRarity.COMMON.label == '普通'

        assert BasicRarity.loads('稀有') == BasicRarity.RARE
        assert BasicRarity.loads(2) == BasicRarity.RARE
        assert BasicRarity.loads(BasicRarity.RARE) == '稀有'
        assert BasicRarity.RARE == 2
        assert BasicRarity.RARE.label == '稀有'

        assert BasicRarity.loads('精锐') == BasicRarity.ELITE
        assert BasicRarity.loads(3) == BasicRarity.ELITE
        assert BasicRarity.loads(BasicRarity.ELITE) == '精锐'
        assert BasicRarity.ELITE == 3
        assert BasicRarity.ELITE.label == '精锐'

        assert BasicRarity.loads('超稀有') == BasicRarity.ULTRA
        assert BasicRarity.loads(4) == BasicRarity.ULTRA
        assert BasicRarity.loads(BasicRarity.ULTRA) == '超稀有'
        assert BasicRarity.ULTRA == 4
        assert BasicRarity.ULTRA.label == '超稀有'

        assert BasicRarity.loads('海上传奇') == BasicRarity.EPIC
        assert BasicRarity.loads(5) == BasicRarity.EPIC
        assert BasicRarity.loads(BasicRarity.EPIC) == '海上传奇'
        assert BasicRarity.EPIC == 5
        assert BasicRarity.EPIC.label == '海上传奇'

        with pytest.raises(ValueError):
            _ = BasicRarity.loads(233)
        with pytest.raises(ValueError):
            _ = BasicRarity.loads('xxx')
        with pytest.raises(TypeError):
            _ = BasicRarity.loads(None)

        assert BasicRarity.EPIC != 233
        assert BasicRarity.EPIC != 'xxx'
        assert BasicRarity.EPIC != None

    def test_research_rarity(self):
        assert ResearchRarity.loads('最高方案') == ResearchRarity.TOP
        assert ResearchRarity.loads(4) == ResearchRarity.TOP
        assert ResearchRarity.loads(ResearchRarity.TOP) == '最高方案'
        assert ResearchRarity.TOP == 4
        assert ResearchRarity.TOP.label == '最高方案'

        assert ResearchRarity.loads('决战方案') == ResearchRarity.DECISIVE
        assert ResearchRarity.loads(5) == ResearchRarity.DECISIVE
        assert ResearchRarity.loads(ResearchRarity.DECISIVE) == '决战方案'
        assert ResearchRarity.DECISIVE == 5
        assert ResearchRarity.DECISIVE.label == '决战方案'

        with pytest.raises(ValueError):
            _ = ResearchRarity.loads(233)
        with pytest.raises(ValueError):
            _ = ResearchRarity.loads('xxx')
        with pytest.raises(TypeError):
            _ = ResearchRarity.loads(None)

        assert ResearchRarity.DECISIVE != 233
        assert ResearchRarity.DECISIVE != 'xxx'
        assert ResearchRarity.DECISIVE != None
