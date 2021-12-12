'''
フェアリーチェス用の駒を集めたモジュール
画像はこちらから一部お借りしています
https://www.chessvariants.com/graphics.dir/alfaerie/index.html

Returns はすべて [(int, int), ...]
'''

from typing import cast

from math_utils import primes, fibos, tribos, tetras, pentas, lucas, pells, perrins
from pieces.pieces import *
from pieces.piece_utils import *


class Custom(Piece):
  '''Piece Dictionary用の駒'''
  abbr = '_'

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return ([(x, y)]
            + [(xx, yy) for xx in range(size) for yy in range(size)
               if no_conflict(gameboard, self.color, xx, yy)])


class Unicorn(Piece):
  abbr = 'Un'
  value = 5.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, rider,
                      (x, y, gameboard, self.color, dir8(1, 2), kwargs['size']))


class Tank(Piece):
  abbr = 'Tk'
  value = 5.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    capture = {(x - 1, y), (x + 1, y)}
    if is_in_bounds(x - 1, y, size) and (x - 1, y) not in gameboard:
      capture |= rider(x - 1, y, gameboard, self.color, [(0, 1), (0, -1)], size)
    if is_in_bounds(x + 1, y, size) and (x + 1, y) not in gameboard:
      capture |= rider(x + 1, y, gameboard, self.color, [(0, 1), (0, -1)], size)
    if kwargs.get('return_capture'):
      return capture

    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      move = rider(x, y, gameboard, self.color, dir8(0, 1), size, move_only=True)
      self.tmp_moves = move | {pos for pos in capture
                               if (pos in gameboard and no_conflict(gameboard, self.color, *pos, size=size))}
    return self.tmp_moves


class Griffin(Piece):
  abbr = 'Gr'
  value = 11.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (leaper(x, y, gameboard, self.color, dir8(1, 1), size=kwargs['size'])
                        | slide_rider(x, y, gameboard, self.color,
                                      [[(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]],
                                      [[(0, 1), (1, 0)], [(1, 0), (0, -1)], [(0, -1), (-1, 0)], [(-1, 0), (0, 1)]],
                                      size=kwargs['size']))
    return self.tmp_moves


class LaserMachine(Piece):
  abbr = 'LM'
  value = 12.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (leaper(x, y, gameboard, self.color, dir8(0, 1), size=kwargs['size'])
                        | slide_rider(x, y, gameboard, self.color,
                                      [[(0, 1)], [(1, 0)], [(0, -1)], [(-1, 0)]],
                                      [[(-1, 1), (1, 1)], [(1, 1), (1, -1)], [(1, -1), (-1, -1)], [(-1, -1), (-1, 1)]],
                                      size=kwargs['size']))
    return self.tmp_moves


class Rhinoceros(Piece):
  abbr = 'Rh'
  value = 12.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (Knight(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_rider(x, y, gameboard, self.color,
                                      [[i] for i in dir8(1, 2)],
                                      sum([[[(1, 1)]] * 2,
                                           [[(1, -1)]] * 2,
                                          [[(-1, -1)]] * 2,
                                          [[(-1, 1)]] * 2], []),
                                      size=kwargs['size']))
    return self.tmp_moves


class Hippopotamus(Piece):
  abbr = 'Hp'
  value = 20.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (Knight(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_rider(x, y, gameboard, self.color,
                                      [[i] for i in dir8(1, 2)],
                                      sum([[[(0, 1), (1, 0)]] * 2,
                                           [[(1, 0), (0, -1)]] * 2,
                                          [[(0, -1), (-1, 0)]] * 2,
                                          [[(-1, 0), (0, 1)]] * 2], []),
                                      size=kwargs['size']))
    return self.tmp_moves


class Tiger(Piece):
  abbr = 'Tg'
  value = 5.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    capture = leaper(x, y, gameboard, self.color,
                     dir8(0, 2) + dir8(1, 2) + dir8(2, 2), size=size)
    if kwargs.get('return_capture'):
      return capture

    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      move = leaper(x, y, gameboard, self.color, list(king_move), move_only=True, size=size)
      self.tmp_moves = move | {pos for pos in capture
                               if (pos in gameboard and no_conflict(gameboard, self.color, *pos, size=size))}
    return self.tmp_moves


class Lion(Piece):
  abbr = 'Lo'
  value = 7.0

  def available_moves(self, x, y, gameboard, **kwargs):
    capture = Queen(self.color).available_moves(x, y, gameboard, **kwargs)
    if kwargs.get('return_capture'):
      return capture

    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      move = King(self.color).available_moves(x, y, gameboard, **kwargs)
      self.tmp_moves = move | {pos for pos in capture
                               if (pos in gameboard and no_conflict(gameboard, self.color, *pos, size=kwargs['size']))}
    return self.tmp_moves


class Deer(Piece):
  abbr = 'De'
  value = 4.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    capture = leaper(x, y, gameboard, self.color, dir8(2, 3), size)
    if kwargs.get('return_capture'):
      return capture

    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      move = leaper(x, y, gameboard, self.color, dir8(1, 2), move_only=True, size=size)
      self.tmp_moves = move | {pos for pos in capture
                               if (pos in gameboard and no_conflict(gameboard, self.color, *pos, size=size))}
    return self.tmp_moves


class Giraffe(Piece):
  abbr = 'Gf'
  value = 5.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color, dir8(1, 4), kwargs['size']))


class Lynx(Piece):
  abbr = 'Lx'
  value = 21.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (Bishop(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_leaper(x, y, gameboard, self.color, size,
                                       [[(i, i) for i in range(1, size)],
                                        [(i, -i) for i in range(1, size)],
                                           [(-i, -i) for i in range(1, size)],
                                           [(-i, i) for i in range(1, size)]],
                                       [dir8(1, 2)[7:] + dir8(1, 2)[:3],
                                           dir8(1, 2)[1:5],
                                           dir8(1, 2)[3:7],
                                           dir8(1, 2)[5:] + dir8(1, 2)[:1]]))
    return self.tmp_moves


class Wave(Piece):
  abbr = 'Wv'
  value = 10.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, wave_rider,
                      (x, y, gameboard, self.color, dir8(1, 1), size))


class Horse(Piece):
  abbr = 'Hs'
  value = 9.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, wave_rider,
                      (x, y, gameboard, self.color, dir8(1, 2), size))


class Donkey(Piece):
  abbr = 'Dn'
  value = 11.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, wave_rider,
                      (x, y, gameboard, self.color, dir8(2, 1), size))


class Octagram(Piece):
  abbr = 'Og'
  value = 8.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (Knight(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_leaper(x, y, gameboard, self.color, size,
                                       [[i] for i in dir8(1, 2)],
                                       [[dir8(1, 2)[6]] + [dir8(1, 2)[2]],
                                           [dir8(1, 2)[7]] + [dir8(1, 2)[3]],
                                           [dir8(1, 2)[0]] + [dir8(1, 2)[4]],
                                           [dir8(1, 2)[1]] + [dir8(1, 2)[5]],
                                           [dir8(1, 2)[2]] + [dir8(1, 2)[6]],
                                           [dir8(1, 2)[3]] + [dir8(1, 2)[7]],
                                           [dir8(1, 2)[4]] + [dir8(1, 2)[0]],
                                           [dir8(1, 2)[5]] + [dir8(1, 2)[1]]]))
    return self.tmp_moves


class ReflectingBishop1(Piece):
  abbr = 'RB'
  value = 10.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, reflect_rider,
                      (x, y, gameboard, self.color, dir8(1, 1), 1, size))


class ReflectingBishop2(Piece):
  abbr = 'RB'
  value = 12.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, reflect_rider,
                      (x, y, gameboard, self.color, dir8(1, 1), 2, size))


class ReflectingBishop3(Piece):
  abbr = 'RB'
  value = 14.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, reflect_rider,
                      (x, y, gameboard, self.color, dir8(1, 1), 3, size))


class ReflectingBishop4(Piece):
  abbr = 'RB'
  value = 18.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, reflect_rider,
                      (x, y, gameboard, self.color, dir8(1, 1), 4, size))


class ReflectingQueen1(Piece):
  abbr = 'RQ'
  value = 18.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (ReflectingBishop1(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Rook(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class ReflectingQueen2(Piece):
  abbr = 'RQ'
  value = 22.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (ReflectingBishop2(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Rook(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class ReflectingQueen3(Piece):
  abbr = 'RQ'
  value = 26.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (ReflectingBishop3(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Rook(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class ReflectingQueen4(Piece):
  abbr = 'RQ'
  value = 30.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (ReflectingBishop4(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Rook(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class PrimeLeaper(Piece):
  abbr = 'PrL'
  value = 29.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in primes], []), kwargs['size']))


class FibonacciLeaper(Piece):
  abbr = 'FL'
  value = 13.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in fibos], []), kwargs['size']))


class TribonacciLeaper(Piece):
  abbr = 'TrL'
  value = 13.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in tribos], []), kwargs['size']))


class TetranacciLeaper(Piece):
  abbr = 'TtL'
  value = 8.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in tetras], []), kwargs['size']))


class PentanacciLeaper(Piece):
  abbr = 'PnL'
  value = 8.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in pentas], []), kwargs['size']))


class LucasLeaper(Piece):
  abbr = 'LL'
  value = 11.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in lucas], []), kwargs['size']))


class PellLeaper(Piece):
  abbr = 'PlL'
  value = 12.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in pells], []), kwargs['size']))


class PerrinLeaper(Piece):
  abbr = 'PeL'
  value = 17.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i) for i in perrins], []), kwargs['size']))


class PythagorasLeaper(Piece):
  abbr = 'PtL'
  value = 25.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color,
                       sum([dist_dir(i ** 2) for i in range(15)], []), kwargs['size']))


class PrimeLeaper2(Piece):
  abbr = 'PrL2'
  value = 23.2

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in primes]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(7)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class FibonacciLeaper2(Piece):
  abbr = 'FL2'
  value = 10.4

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in fibos]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(8)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class TribonacciLeaper2(Piece):
  abbr = 'TrL2'
  value = 10.4

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in tribos]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(7)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class TetranacciLeaper2(Piece):
  abbr = 'TtL2'
  value = 6.4

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in tetras]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(6)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class PentanacciLeaper2(Piece):
  abbr = 'PnL2'
  value = 6.4

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in pentas]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(7)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class LucasLeaper2(Piece):
  abbr = 'LL2'
  value = 8.8

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in lucas]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(6)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class PellLeaper2(Piece):
  abbr = 'PlL2'
  value = 9.6

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in pells]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(5)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class PerrinLeaper2(Piece):
  abbr = 'PeL2'
  value = 13.6

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = [dist_dir(i) for i in perrins]
      a = cast('list[PositionList]', a)
      _ = [{tuple(k[m] for k in a if k != [])[:j]:
            [[k[m] for k in a if k != []][j]]
            for j in range(9)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


class PythagorasLeaper2(Piece):
  abbr = 'PtL2'
  value = 8.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      a = sum([k for k in
               [dist_dir(i ** 2, sep=True) for i in range(1, 15)]
               if k != []], [])
      a = cast('list[PositionList]', a)
      _ = [{tuple(i[m] for i in a)[:j]:
            [[i[m] for i in a][j]]
            for j in range(14)} for m in range(8)]
      self.tmp_moves = set()
      for i in range(8):
        self.tmp_moves |= slide_leaper(x, y, gameboard, self.color, size,
                                       list(map(list, _[i].keys())),
                                       list(_[i].values()),
                                       absolute='dest')
    return self.tmp_moves


# 動きテスト用
class Tst(Piece):
  abbr = 'Tst'
  value = 0.0
  archer_dir = [-2, -1, 1, 2]

  def available_moves(self, x, y, gameboard, **kwargs):
    return moves_from('+,x,2+,2x', x, y, gameboard, self.color, size=kwargs['size'])
