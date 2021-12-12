'''ゲームの種類によって変わる駒の配置や名前、画像IDを記録したモジュール'''

import os

from random import randint
from typing import List, Union, Type, TypedDict, cast
import yaml

from custom_types import Color, Placers, AsymPlacers
from pieces.index import *


PromotionTargetCollection = List[Type[Piece]]


GameYml = TypedDict('GameYml', {
    'name': str,
    'size': int,
    'castling': bool,
    'promote2': 'list[str]',
    'asym': bool,
    'placers': Union[
        'dict[int, list[Optional[str]]]',
        'dict[int, list[Optional[tuple[str, Color]]]]',
    ],
})


GameType = TypedDict('Game', {
    'name': str,
    'size': int,
    'castling': bool,
    'asym': bool,
    'promote2': PromotionTargetCollection,
    'placers': Union[Placers, AsymPlacers],
})

_file_nums = len(os.listdir('main/games'))
games: List[GameType] = []

for i in range(_file_nums):
  with open(f'main/games/{i+1}.yml', encoding='utf8') as file:
    _yml: List[GameYml] = yaml.safe_load(file)
    _game_list = cast(List[GameType], copy(_yml))
    for index, game in enumerate(_yml):
      _game_list[index]['promote2'] = [globals()[piece] for piece in game['promote2']]
      if game['asym']:
        placers = cast('dict[int, list[Optional[tuple[str, Color]]]]', game['placers'])
        _game_list[index]['placers'] = cast(AsymPlacers, {
            num: tuple(
                ((globals()[piece[0]], piece[1]) if piece is not None else None) for piece in piece_list
            ) for num, piece_list in placers.items()
        })
      else:
        placers = cast('dict[int, list[Optional[str]]]', game['placers'])
        _game_list[index]['placers'] = cast(Placers, {
            num: tuple(
                (globals()[piece] if piece is not None else None) for piece in piece_list
            ) for num, piece_list in placers.items()
        })
      for placers in _game_list[index]['placers'].values():
        assert len(placers) == _game_list[index]['size']
    games += _game_list


_krns: 'list[list[Type[Piece]]]' = [
    [Knight, Knight, Rook, King, Rook],
    [Knight, Rook, Knight, King, Rook],
    [Knight, Rook, King, Knight, Rook],
    [Knight, Rook, King, Rook, Knight],
    [Rook, Knight, Knight, King, Rook],
    [Rook, Knight, King, Knight, Rook],
    [Rook, Knight, King, Rook, Knight],
    [Rook, King, Knight, Knight, Rook],
    [Rook, King, Knight, Rook, Knight],
    [Rook, King, Rook, Knight, Knight],
]


def init_960():
  '''チェス 960 における駒の配置の決定'''
  pos_id = randint(0, 959)
  while pos_id == 518:
    pos_id = randint(0, 959)

  placers: 'list[Optional[Type[Piece]]]' = [None] * 8

  q, r = pos_id // 4, pos_id % 4
  placers[2 * r + 1] = Bishop

  q, r = q // 4, q % 4
  placers[2 * r] = Bishop

  q, r = q // 6, q % 6
  for i in range(8):
    if placers[i] is None:
      if i == r:
        placers[i] = Queen
        break
    else:
      r += 1

  for piece in _krns[q]:
    placers[placers.index(None)] = piece

  return tuple(placers)
