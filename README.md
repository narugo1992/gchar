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

### Game Character Query

Find the characters (nicknames are supported for arknights and fgo)

Currently Supported Games (If you need data of other games,
you can [create an issue](https://github.com/narugo1992/gchar/issues/new)):

* Arknights (crawled from [PRTS Wiki](https://prts.wiki))
* Fate/Grand Order (crawled from [FGO Wiki](https://fgo.wiki))
* Azur Lane (crawled from [BiliGame Wiki](https://wiki.biligame.com/blhx))
* Girls' Front-Line (crawled from [IOPWiki](https://iopwiki.com/))
* Genshin Impact (crawled from [Fandom](https://genshin-impact.fandom.com/ja/wiki/%E5%8E%9F%E7%A5%9E_Wiki))
* Neural Cloud (crawled from [42lab wiki](http://wiki.42lab.cloud))
* Blue Archive (crawled from [bluearchive wiki](https://bluearchive.wiki/) and [Gamekee BA](https://ba.gamekee.com))
* Nikke: Goddess of Victory (crawled from [Fandom](https://nikke-goddess-of-victory-international.fandom.com)
  and [Gamekee Nikke](https://nikke.gamekee.com))
* Path To Nowhere (crawled from [BiliGame Wiki](https://wiki.biligame.com/wqmt))
* Honkai: Star Rail (crawled from [Star Rail Station](https://starrailstation.com)
  and [BiliGame Wiki](https://wiki.biligame.com))

```
>>> from gchar.games import get_character
>>> 
>>> get_character('amiya')  # english name
<Character R001 - 阿米娅/amiya/アーミヤ, female, 5*****>
>>> get_character('z18')
<Character 346 - Z18/hans_ludemann/ハンス・リューデマン, 稀有(2**), group: Group.KMS>
>>> get_character('416')
<Character 65 - HK416/416/416, 5*****, clazz: Clazz.AR>
>>> 
>>> get_character('夕')  # chinese name
<Character NM02 - 夕/dusk/シー, female, 6******>
>>> get_character('宵宫')
<Character 宵宫/yoimiya/宵宮/よいみや, female, 5*****, weapon: Weapon.BOW, element: Element.PYRO>
>>> 
>>> get_character('スルト')  # japanese name
<Character R111 - 史尔特尔/surtr/スルト, female, 6******>
>>> 
>>> get_character('CEO')  # alias
<Character 171 - 彭忒西勒亚/黄金国的Berserker/penthesilea/berserker_of_el_dorado/ペンテシレイア/エルドラドのバーサーカー, female, 4****, class: Clazz.BERSERKER>
>>> get_character('黑呆')
<Character 3 - 阿尔托莉雅·潘德拉贡〔Alter〕/altria_pendragon_alter/アルトリア・ペンドラゴン〔オルタ〕/アルトリア・ペンドラゴン・オルタ/アルトリア・オルタ, female, 4****, class: Clazz.SABER>
>>> get_character('小火龙')
<Character RL03 - 伊芙利特/ifrit/イフリータ, female, 6******>
```

List all character with specific condition of one game

```python
from gchar.games.arknights import Character

for ch in Character.all():  # 5star, boys
    if ch.rarity == 5 and ch.gender == 'male':
        print(ch)

```

### Pixiv Resources

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

See how many posts on pixiv

```
>>> from gchar.resources.pixiv import get_pixiv_posts
>>> 
>>> # first one is all, second one is r18
>>> get_pixiv_posts('CEO')
(867, 113)
>>> get_pixiv_posts('黑贞')
(21908, 3820)
>>> get_pixiv_posts('amiya')
(14130, 1113)
>>> get_pixiv_posts('blazer')  # fuzzy match is supported, but slower
(1967, 383)
>>> get_pixiv_posts('林雨霞')
(259, 44)
>>> get_pixiv_posts('夕')
(2908, 424)
```

### Other Sites' Resource

Get tags for danbooru and other sites

Currently supported sites:

* [Anime Pictures](https://anime-pictures.net), named `anime_pictures`
* [Atfbooru](https://booru.allthefallen.moe), named `atfbooru`
* [Sankaku](https://chan.sankakucomplex.com), named `sankaku`
* [Danbooru](https://danbooru.donmai.us), named `danbooru`
* [Hypnohub](https://hypnohub.net), named `hypnohub`
* [Konachan](https://konachan.com), named `konachan`
* [Konachan.Net](https://konachan.net), named `konachan_net`
* [Lolibooru](https://lolibooru.moe), named `lolibooru`
* [Rule34](https://rule34.xxx), named `rule34`
* [Safebooru](https://safebooru.donmai.us), named `safebooru`
* [Xbooru](https://xbooru.com), named `xbooru`
* [Yande](https://yande.re), named `yande`
* [Zerochan](https://zerochan.net), named `zerochan`
* [WallHaven](https://wallhaven.cc), named `wallhaven` (`id:xxxx` will be used for explicit searching)

```
>>> from gchar.resources.sites import get_site_tag
>>> 
>>> # first one is all, second one is r18
>>> get_site_tag('CEO', 'danbooru')
'penthesilea_(fate)'
>>> get_site_tag('黑贞', 'danbooru')
"jeanne_d'arc_alter_(fate)"
>>> get_site_tag('amiya', 'danbooru')
'amiya_(arknights)'
>>> get_site_tag('林雨霞', 'danbooru')
'lin_(arknights)'
>>> get_site_tag('夕', 'danbooru')
'dusk_(arknights)'
>>> get_site_tag('夕', 'danbooru', with_posts=True)  # see how many images
('dusk_(arknights)', 1397)
>>> get_site_tag('夕', 'zerochan')  # another sites
'Dusk (Arknights)'
```

## FAQ

Q: How timely is the data?

A: The data is updated approximately once a day and is hosted on Github Action, ensuring its timeliness. In the event of
a malfunction on the crawled Wiki site that prevents data updates, the corresponding Wiki team will be contacted to
resolve the issue.

