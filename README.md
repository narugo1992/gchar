# gchar

[![PyPI](https://img.shields.io/pypi/v/gchar)](https://pypi.org/project/gchar/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gchar)
![Loc](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/narugo1992/254442dea2e77cf46366df97f499242f/raw/loc.json)
![Comments](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/narugo1992/254442dea2e77cf46366df97f499242f/raw/comments.json)
[![Last Updated](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/narugo1992/254442dea2e77cf46366df97f499242f/raw/data_last_update.json)](https://huggingface.co/datasets/deepghs/game_characters)

[![Code Test](https://github.com/narugo1992/gchar/workflows/Code%20Test/badge.svg)](https://github.com/narugo1992/gchar/actions?query=workflow%3A%22Code+Test%22)
[![Data Publish](https://github.com/narugo1992/gchar/actions/workflows/data.yml/badge.svg)](https://github.com/narugo1992/gchar/actions/workflows/data.yml)
[![Package Release](https://github.com/narugo1992/gchar/workflows/Package%20Release/badge.svg)](https://github.com/narugo1992/gchar/actions?query=workflow%3A%22Package+Release%22)
[![codecov](https://codecov.io/gh/narugo1992/gchar/branch/main/graph/badge.svg?token=XJVDP4EFAT)](https://codecov.io/gh/narugo1992/gchar)

![GitHub Org's stars](https://img.shields.io/github/stars/narugo1992)
[![GitHub stars](https://img.shields.io/github/stars/narugo1992/gchar)](https://github.com/narugo1992/gchar/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/narugo1992/gchar)](https://github.com/narugo1992/gchar/network)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/narugo1992/gchar)
[![GitHub issues](https://img.shields.io/github/issues/narugo1992/gchar)](https://github.com/narugo1992/gchar/issues)
[![GitHub pulls](https://img.shields.io/github/issues-pr/narugo1992/gchar)](https://github.com/narugo1992/gchar/pulls)
[![Contributors](https://img.shields.io/github/contributors/narugo1992/gchar)](https://github.com/narugo1992/gchar/graphs/contributors)
[![GitHub license](https://img.shields.io/github/license/narugo1992/gchar)](https://github.com/narugo1992/gchar/blob/master/LICENSE)

Database of known game characters. The database is refreshed once a day, hosted
on [huggingface - deepghs/game_characters](https://huggingface.co/datasets/deepghs/game_characters).

## Installation

You can install `gchar` with pip

```shell
pip install gchar
```

## Quick Start

Find the characters (nicknames are supported for arknights and fgo)

```
>>> from gchar.games import get_character
>>> 
>>> get_character('CEO')
<Character 171 - 彭忒西勒亚/黄金国的berserker/penthesilea/berserker_of_el_dorado/ペンテシレイア/エルドラドのバーサーカー, female, 4****>
>>> get_character('黑呆')
<Character 3 - 阿尔托莉雅·潘德拉贡〔alter〕/altria_pendragon_alter/アルトリア・ペンドラゴン〔オルタ〕, female, 4****>
>>> get_character('amiya')
<Character R001 - 阿米娅/amiya/アーミヤ, female, 5*****>
>>> get_character('小火龙')
<Character RL03 - 伊芙利特/ifrit/イフリータ, female, 6******>
>>> get_character('宵宫')
<Character 宵宫/yoimiya/宵宮/よいみや, female, 5*****, weapon: Weapon.BOW, element: Element.PYRO>
>>> get_character('z18')
<Character 346 - z18/hans_ludemann/ハンス・リューデマン, 稀有(2**), group: Group.KMS>
>>> get_character('416')
<Character 65 - HK416/416/416, 5*****, clazz: Clazz.AR>
```

List all character with specific condition of one game

```python
from gchar.games.arknights import Character

for ch in Character.all():  # 5star, boys
    if ch.rarity == 5 and ch.gender == 'male':
        print(ch)

```

Get search keywords for pixiv

```
>>> from gchar.resources.pixiv import get_pixiv_keywords
>>> 
>>> get_pixiv_keywords('CEO')
'Fate/GrandOrder (berserker_of_el_dorado OR penthesilea OR エルドラドのバーサーカー OR ペンテシレイア OR 彭忒西勒亚 OR 黄金国的berserker)'
>>> get_pixiv_keywords('黑贞')
'Fate/GrandOrder (jeanne_d_arc_alter OR ジャンヌ・ダルク〔オルタ〕 OR 贞德〔alter〕) -jeanne_d_arc_alter_santa_lily'
>>> get_pixiv_keywords('amiya')
'アークナイツ (amiya OR アーミヤ OR 阿米娅)'
>>> get_pixiv_keywords('blazer')  # fuzzy match is supported
'アークナイツ (blaze OR ブレイズ OR 煌)'
>>> get_pixiv_keywords('林雨霞')
'アークナイツ (lin OR 林) -angelina -flint -folinic -ling -守林人 -巡林者 -杜林'
>>> get_pixiv_keywords('夕')
'アークナイツ (dusk OR シー OR 夕) -ケルシー -シージ -シーン'
```

Get tags for danbooru

```
>>> from gchar.resources.danbooru import get_danbooru_tag
>>> 
>>> get_danbooru_tag('CEO')
'penthesilea_(fate)'
>>> get_danbooru_tag('黑贞')
"jeanne_d'arc_alter_(fate)"
>>> get_danbooru_tag('amiya')
'amiya_(arknights)'
>>> get_danbooru_tag('blazer')  # fuzzy match is supported
'blaze_(arknights)'
>>> get_danbooru_tag('林雨霞')
'lin_(arknights)'
>>> get_danbooru_tag('夕')
'dusk_(arknights)'
```

Currently Supported Games (If you need data of other games,
you can [create an issue](https://github.com/narugo1992/gchar/issues/new)):

* Arknights (crawled from [https://prts.wiki](https://prts.wiki))
* Fate/Grand Order (crawled from [https://fgo.wiki](https://fgo.wiki))
* Azur Lane (crawled from [https://wiki.biligame.com/blhx](https://wiki.biligame.com/blhx))
* Girls' Front-Line (crawled from [https://iopwiki.com/](https://iopwiki.com/))
* Genshin Impact (crawled
  from [https://genshin-impact.fandom.com/ja/wiki/%E5%8E%9F%E7%A5%9E_Wiki](https://genshin-impact.fandom.com/ja/wiki/%E5%8E%9F%E7%A5%9E_Wiki))

## FAQ

### The data here is out-of-date

Just update the local data with the following commands.

```shell
python -m gchar update        # download newest data of all the games
python -m gchar update -g fgo # download newest data of fgo
python -m gchar update --help # help information

```

