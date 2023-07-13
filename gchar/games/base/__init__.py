"""
Overview:
    Character basic modeling, including the character model itself, the character name,
    the character gender, and the character skins.
"""
from .character import Character, list_all_characters
from .name import ChineseName, EnglishName, JapaneseName, TextName, SegmentName
from .property import Gender
from .skin import Skin
