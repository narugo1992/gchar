from ._base import _BaseGenericCharacter
from ..games import register_game


class Character(_BaseGenericCharacter):
    __game_name__ = 'lovelivesuperstar'
    __official_name__ = 'Love Live! Superstar!!'
    __game_keywords__ = ['Love Live! Superstar!!', 'Love Live! (new Project)', 'Love Live! Superstar!', 'Love Live! Superstar', 'ラブライブ!スーパースター!!', 'ラブライブ！スーパースター!!', 'raburaibu!supasuta!!']
    __pixiv_keyword__ = 'ラブライブ!スーパースター!!'
    __pixiv_suffix__ = 'ラブライブ!スーパースター!!'


register_game(Character)

