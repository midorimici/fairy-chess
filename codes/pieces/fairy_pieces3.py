'''
フェアリーチェス用の駒を集めたモジュール
特殊な駒たち

Returns はすべて [(int, int), ...]
'''

from copy import copy
from typing import Literal, Union, Optional, Type, cast

from custom_types import Color, PositionList, Board
from math_utils import is_prime, knacci
from pieces.pieces import *
from pieces.piece_utils import *


'動かした回数によって動きが変わる'


class DevelopingMan(Piece):
  abbr = 'DM'
  value = 0.0

  def __init__(self, color):
    super().__init__(color)
    self.count = 0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper, (x, y, gameboard, self.color,
                                          sum([dist_dir(i) for i in range(1, self.count + 2)], []),
                                          kwargs['size']))


class NacciLeaper(Piece):
  abbr = 'NL'
  value = 16.0

  def __init__(self, color):
    super().__init__(color)
    self.count = 0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper, (x, y, gameboard, self.color,
                                          sum([dist_dir(k) for k in (
                                              [knacci(self.count + 2, i) for i in range(1, self.count + 12)]
                                              if self.count <= 6 else [2 ** i for i in range(9)])], []),
                                          kwargs['size']))


class DevelopingPrime(Piece):
  abbr = 'DP'
  value = 0.0

  def __init__(self, color):
    super().__init__(color)
    self.count = 0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper, (x, y, gameboard, self.color,
                                          sum([dist_dir(i) for i in range(2, self.count + 3) if is_prime(i)], []),
                                          kwargs['size']))


class DevelopingMan2(Piece):
  abbr = 'DM2'
  value = 0.0

  def __init__(self, color):
    super().__init__(color)
    self.count = 0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = sum([k for k in [dist_dir(i, sep=True) for i in range(1, self.count + 2)] if k != []], [])
      a = cast('list[PositionList]', a)
      lenA = len(a)
      _ = [{tuple(i[m] for i in a)[:j]: [[i[m] for i in a][j]] for j in range(lenA)}
           for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class NacciLeaper2(Piece):
  abbr = 'NL2'
  value = 12.8

  def __init__(self, color):
    super().__init__(color)
    self.count = 0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = sum([k for k in [dist_dir(j, sep=True)
              for j in ([knacci(self.count + 2, i) for i in range(1, self.count + 12)]
              if self.count <= 6 else [2 ** i for i in range(9)])]
          if k != [] and k != [[(0, 0)] * 8]], [])
      a = cast('list[PositionList]', a)
      lenA = len(a)
      _ = [{tuple(i[m] for i in a)[:j]:
            [[i[m] for i in a][j]]
            for j in range(lenA)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class Imitator(Piece):
  abbr = 'It'
  value = 5.0

  def __init__(self, color):
    super().__init__(color)
    self.count = 0

  def available_moves(self, x, y, gameboard, **kwargs):
    move = None
    if self.count % 5 == 0:
      move = Knight(self.color).available_moves(x, y, gameboard, **kwargs)
    if self.count % 5 == 1:
      move = Bishop(self.color).available_moves(x, y, gameboard, **kwargs)
    if self.count % 5 == 2:
      move = Rook(self.color).available_moves(x, y, gameboard, **kwargs)
    if self.count % 5 == 3:
      move = Queen(self.color).available_moves(x, y, gameboard, **kwargs)
    if self.count % 5 == 4:
      move = King(self.color).available_moves(x, y, gameboard, **kwargs)
    assert move is not None
    return move


'周りに影響を与える'


class Mist(Piece):
  abbr = 'Mi'
  value = 4.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, rider,
                      (x, y, gameboard, self.color, dir8(0, 1), kwargs['size'], 2, False, True))


class Blizzard(Piece):
  abbr = 'Bz'
  value = 8.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, moves_from,
                      ('2+', x, y, gameboard, self.color, kwargs['size']))


'周りの駒によって動きが変わる'


class Orphan(Piece):
  abbr = 'Op'
  value = 10.0

  def __init__(self, color):
    super().__init__(color)
    self.tmp_potentials: 'set[Type[Piece]]' = set()
    self.res_potentials: 'set[Type[Piece]]' = set()
    # ↓ 完成された値しか入れない
    self.compounded_normal_pieces_memo: 'Optional[set[Type[Piece]]]' = None

  def compounded_normal_pieces(self, x: int, y: int, gameboard: Board, size: int) -> 'set[Type[Piece]]':
    '''
    フレンド・オーファン以外の駒で動きを受け取るものの集合を返す
    '''
    if self.compounded_normal_pieces_memo:
      return self.compounded_normal_pieces_memo

    ret: 'set[Type[Piece]]' = set()
    for pos, piece in gameboard.items():
      # 対象が敵の駒であってフレンド・オーファンでない
      # 対象の駒に攻撃されている
      if (piece.color != self.color and piece.abbr not in ('Fr', 'Op')
              and (x, y) in piece.available_moves(*pos, gameboard, size=size)):
        # その駒の種類を追加
        ret.add(type(piece))
    self.compounded_normal_pieces_memo = ret
    return ret

  def give_moves(self, x: int, y: int, gameboard: Board, size: int):
    '''
    「自分が攻撃している敵のオーファン」または「自分が守っている味方のフレンド」が
    自分と同じ動きをしていないなら、自分の動きを付与
    tmp_moves を更新
    '''
    opponent: 'dict[Color, Color]' = {'W': 'B', 'B': 'W'}

    pot = self.compounded_normal_pieces(x, y, gameboard, size)
    self.tmp_potentials |= pot
    if self.tmp_moves == set():
      for piece in self.tmp_potentials:
        self.tmp_moves |= piece(self.color).available_moves(x, y, gameboard, size=size)
    _propagate(self, self.color, 'Op', x, y, gameboard, size)
    _propagate(self, opponent[self.color], 'Fr', x, y, gameboard, size)

  def available_moves(self, x: int, y: int, gameboard: Board, **kwargs):
    return self.tmp_moves


class Friend(Piece):
  abbr = 'Fr'
  value = 10.0

  def __init__(self, color):
    super().__init__(color)
    self.tmp_potentials: 'set[Type[Piece]]' = set()
    self.res_potentials: 'set[Type[Piece]]' = set()
    # ↓ 完成された値しか入れない
    self.compounded_normal_pieces_memo: 'Optional[set[Type[Piece]]]' = None

  def compounded_normal_pieces(self, x: int, y: int, gameboard: Board, size: int) -> 'set[Type[Piece]]':
    '''
    フレンド・オーファン以外の駒で動きを受け取るものの集合を返す
    '''
    if self.compounded_normal_pieces_memo:
      return self.compounded_normal_pieces_memo

    opponent = {'W': 'B', 'B': 'W'}
    ret: 'set[Type[Piece]]' = set()
    tmp_board = copy(gameboard)
    tmp_board[(x, y)] = type(self)(opponent[self.color])
    for pos, piece in gameboard.items():
      # 対象が味方の駒であってフレンド・オーファンでない
      # 対象の駒に守られている
      if (piece.color == self.color and piece.abbr not in ('Fr', 'Op')
          and (x, y) in piece.available_moves(
              *pos, tmp_board, size=size)):
        # その駒の種類を追加
        ret.add(type(piece))
    self.compounded_normal_pieces_memo = ret
    return ret

  def give_moves(self, x: int, y: int, gameboard: Board, size: int):
    '''
    「自分が守っている味方のフレンド」または「自分が攻撃している敵のオーファン」が
    自分と同じ動きをしていないなら、自分の動きを付与
    tmp_moves を更新
    '''
    opponent: 'dict[Color, Color]' = {'W': 'B', 'B': 'W'}

    pot = self.compounded_normal_pieces(x, y, gameboard, size)
    self.tmp_potentials |= pot
    if self.tmp_moves == set():
      for piece in self.tmp_potentials:
        self.tmp_moves |= piece(self.color).available_moves(x, y, gameboard, size=size)
    _propagate(self, opponent[self.color], 'Fr', x, y, gameboard, size)
    _propagate(self, self.color, 'Op', x, y, gameboard, size)

  def available_moves(self, x: int, y: int, gameboard: Board, **kwargs):
    return self.tmp_moves


def _propagate(self: Union[Orphan, Friend], color: Color, abbr: Literal['Op', 'Fr'],
               x: int, y: int, gameboard: Board, size: int):
  opponent: 'dict[Color, Color]' = {'W': 'B', 'B': 'W'}

  _moves: PositionSet = set()
  for piece in self.tmp_potentials:
    _moves |= piece(color).available_moves(x, y, gameboard, size=size)

  for pos in _moves:
    target = gameboard.get(pos)
    if target is None or target.abbr != abbr:
      continue

    target = cast(Union[Orphan, Friend], target)
    if target.tmp_potentials == set():
      target.tmp_potentials |= target.compounded_normal_pieces(*pos, gameboard, size)
    if target.tmp_potentials != self.tmp_potentials:
      target.tmp_potentials |= self.tmp_potentials
      _propagate(target, target.color, 'Op', *pos, gameboard, size)
      _propagate(target, opponent[target.color], 'Fr', *pos, gameboard, size)
    if target.tmp_potentials != target.res_potentials:
      target.res_potentials |= target.tmp_potentials
      _res_moves: PositionSet = set()
      for piece in target.res_potentials:
        _res_moves |= piece(target.color).available_moves(*pos, gameboard, size=size)
      target.tmp_moves = _res_moves


'動いた後に攻撃する（アーチャー系）'


class Archer(Piece):
  abbr = 'Ar'
  value = 6.0
  # 矢を発射する角度．
  # 2 が左，0 が前，-2 が右，4 が後ろ．
  # 1  0  -1
  # 2  Λ  -2
  # 3  4  -3
  archer_dir = [-2, -1, 0, 1, 2]

  def available_moves(self, x, y, gameboard, **kwargs):
    self.direction = 1 if self.color == 'W' else -1
    return self.prune(gameboard, moves_from,
                      (f'{self.direction}/0', x, y, gameboard, self.color, kwargs['size']))


class HorseArcher(Piece):
  abbr = 'HA'
  value = 9.0
  archer_dir = [-2, -1, 1, 2]

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, moves_from,
                      ('+,x,2+,2x', x, y, gameboard, self.color, kwargs['size']))
