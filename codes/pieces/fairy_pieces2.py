'''
フェアリーチェス用の駒を集めたモジュール
Noble Chess セット

Returns はすべて [(int, int), ...]
'''


from pieces.pieces import *
from pieces.piece_utils import *


class Esquire(Piece):
  abbr = 'Es'
  value = 2.5

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]],
                          [[(0, 1), (1, 0)], [(1, 0), (0, -1)], [(0, -1), (-1, 0)], [(-1, 0), (0, 1)]]))


class Esquiress(Piece):
  abbr = 'Ess'
  value = 2.5

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[(0, 1)], [(1, 0)], [(0, -1)], [(-1, 0)]],
                          [[(-1, 1), (1, 1)], [(1, 1), (1, -1)], [(1, -1), (-1, -1)], [(-1, -1), (-1, 1)]]))


class Knightess(Piece):
  abbr = 'Nts'
  value = 3.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, moves_from,
                      ('2+,2x', x, y, gameboard, self.color, kwargs['size']))


class Baronet(Piece):
  abbr = 'Bt'
  value = 3.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[i] for i in king_move],
                          [[(-1, 1), (1, 1)],
                           [(1, 1)],
                           [(1, 1), (1, -1)],
                           [(1, -1)],
                           [(1, -1), (-1, -1)],
                           [(-1, -1)],
                           [(-1, -1), (-1, 1)],
                           [(-1, 1)]]))


class Baronetess(Piece):
  abbr = 'Bts'
  value = 3.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]],
                          [king_move[:3],
                           king_move[2:5],
                           king_move[4:7],
                           king_move[6:] + king_move[:1]]))


class Baron(Piece):
  abbr = 'Br'
  value = 3.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[i] for i in king_move],
                          [[(0, 1)],
                           [(0, 1), (1, 0)],
                           [(1, 0)],
                           [(1, 0), (0, -1)],
                           [(0, -1)],
                           [(0, -1), (-1, 0)],
                           [(-1, 0)],
                           [(-1, 0), (0, 1)]]))


class Baroness(Piece):
  abbr = 'Brs'
  value = 3.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[(0, 1)], [(1, 0)], [(0, -1)], [(-1, 0)]],
                          [king_move[7:] + king_move[:2],
                           king_move[1:4],
                           king_move[3:6],
                           king_move[5:]]))


class Viscount(Piece):
  abbr = 'Vs'
  value = 4.5

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (King(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Baron(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class Viscountess(Piece):
  abbr = 'Vss'
  value = 4.5

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (leaper(x, y, gameboard, self.color, dir8(0, 1), kwargs['size'])
                        | Baroness(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class Count(Piece):
  abbr = 'Ct'
  value = 5.0

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[i] for i in king_move],
                          [dir8(1, 2)[6:] + dir8(1, 2)[:2],
                           dir8(1, 2)[7:] + dir8(1, 2)[:3],
                           dir8(1, 2)[:4],
                           dir8(1, 2)[1:5],
                           dir8(1, 2)[2:6],
                           dir8(1, 2)[3:7],
                           dir8(1, 2)[4:],
                           dir8(1, 2)[5:] + dir8(1, 2)[:1]]))


class Countess(Piece):
  abbr = 'Cts'
  value = 5.5

  def available_moves(self, x, y, gameboard, **kwargs):
    size = kwargs['size']
    return self.prune(gameboard, slide_leaper,
                      (x, y, gameboard, self.color, size,
                       [[i] for i in dir8(1, 2)],
                          [king_move[7:] + king_move[:3],
                           king_move[:4],
                           king_move[1:5],
                           king_move[2:6],
                           king_move[3:7],
                           king_move[4:],
                           king_move[5:] + king_move[:1],
                           king_move[6:] + king_move[:2]]))


class Burggraf(Piece):
  abbr = 'Bg'
  value = 4.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (King(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_leaper(x, y, gameboard, self.color, size,
                                       [[i] for i in king_move],
                                       [dir8(1, 1), dir8(0, 1)] * 4))
    return self.tmp_moves


class Burggräfin(Piece):
  abbr = 'Bgn'
  value = 4.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (King(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_leaper(x, y, gameboard, self.color, size,
                                       [[i] for i in king_move],
                                       [dir8(0, 1), dir8(1, 1)] * 4))
    return self.tmp_moves


class Pfalzgraf(Piece):
  abbr = 'Pg'
  value = 7.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (King(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_leaper(x, y, gameboard, self.color, size,
                                       [[i] for i in king_move],
                                       [king_move[7:] + king_move[:2],
                                           king_move[:3],
                                           king_move[1:4],
                                           king_move[2:5],
                                           king_move[3:6],
                                           king_move[4:7],
                                           king_move[5:],
                                           king_move[6:] + king_move[:1]]))
    return self.tmp_moves


class Pfalzgräfin(Piece):
  abbr = 'Pgn'
  value = 7.2

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (King(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_leaper(x, y, gameboard, self.color, size,
                                       [[i] for i in king_move],
                                       [king_move] * 8))
    return self.tmp_moves


class Landgraf(Piece):
  abbr = 'Lg'
  value = 12.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (rider(x, y, gameboard, self.color, king_move, size, length=2)
                        | slide_leaper(x, y, gameboard, self.color, size,
                                       [[(i, j), (2 * i, 2 * j)] for i, j in king_move],
                                       [[(-1, 1), (1, 1)],
                                           [(0, 1), (1, 0)],
                                           [(1, 1), (1, -1)],
                                           [(1, 0), (0, -1)],
                                           [(1, -1), (-1, -1)],
                                           [(0, -1), (-1, 0)],
                                           [(-1, -1), (-1, 1)],
                                           [(-1, 0), (0, 1)]]))
    return self.tmp_moves


class Landgräfin(Piece):
  abbr = 'Lgn'
  value = 10.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (King(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_rider(x, y, gameboard, self.color,
                        [[i] for i in king_move],
          [[(-1, 1), (1, 1)],
                            [(0, 1), (1, 0)],
                            [(1, 1), (1, -1)],
                            [(1, 0), (0, -1)],
                            [(1, -1), (-1, -1)],
                            [(0, -1), (-1, 0)],
                            [(-1, -1), (-1, 1)],
                            [(-1, 0), (0, 1)]],
          length=2, size=kwargs['size']))
    return self.tmp_moves


class Markgraf(Piece):
  abbr = 'Mg'
  value = 10.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (King(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Count(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class Markgräfin(Piece):
  abbr = 'Mgn'
  value = 11.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (Knight(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Countess(self.color).available_moves(x, y, gameboard, **kwargs))
    return self.tmp_moves


class Marquis(Piece):
  abbr = 'Mq'
  value = 17.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (Bishop(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Knight(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_rider(x, y, gameboard, self.color,
                                      [[i] for i in dir8(1, 2)],
                                      sum([[[(0, 1), (1, 0)]] * 2,
                                           [[(1, 0), (0, -1)]] * 2,
                                          [[(0, -1), (-1, 0)]] * 2,
                                          [[(-1, 0), (0, 1)]] * 2], []),
                                      length=2, size=kwargs['size']))
    return self.tmp_moves


class Marchioness(Piece):
  abbr = 'Mcs'
  value = 15.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (Rook(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Knight(self.color).available_moves(x, y, gameboard, **kwargs)
                        | slide_rider(x, y, gameboard, self.color,
                                      [[i] for i in dir8(1, 2)],
                                      sum([[[(1, 1)]] * 2,
                                           [[(1, -1)]] * 2,
                                          [[(-1, -1)]] * 2,
                                          [[(-1, 1)]] * 2], []),
                                      length=2, size=kwargs['size']))
    return self.tmp_moves


class Duke(Piece):
  abbr = 'Dk'
  value = 18.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (slide_leaper(x, y, gameboard, self.color, size,
                                     [[(i, i) for i in range(1, size)],
                                      [(i, -i) for i in range(1, size)],
                                         [(-i, -i) for i in range(1, size)],
                                         [(-i, i) for i in range(1, size)]],
                                     [dir8(0, 1)] * 4)
                        | slide_rider(x, y, gameboard, self.color,
                                      [[(0, 1)], [(1, 0)], [(0, -1)], [(-1, 0)]],
                                      [dir8(1, 1)] * 4))
    return self.tmp_moves


class Duchess(Piece):
  abbr = 'Dcs'
  value = 19.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      size = kwargs['size']
      self.tmp_moves = (slide_leaper(x, y, gameboard, self.color, size,
                                     [[(0, i) for i in range(1, size)],
                                      [(i, 0) for i in range(1, size)],
                                         [(0, -i) for i in range(1, size)],
                                         [(-i, 0) for i in range(1, size)]],
                                     [dir8(1, 1)] * 4)
                        | slide_rider(x, y, gameboard, self.color,
                                      [[(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]],
                                      [dir8(0, 1)] * 4))
    return self.tmp_moves


class GrandDuke(Piece):
  abbr = 'GDk'
  value = 22.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (Duke(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Bishop(self.color).available_moves(x, y, gameboard, **kwargs)
                        | leaper(x, y, gameboard, self.color, dir8(0, 1), size=kwargs['size']))
    return self.tmp_moves


class GrandDuchess(Piece):
  abbr = 'GDcs'
  value = 27.0

  def available_moves(self, x, y, gameboard, **kwargs):
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves = (Duchess(self.color).available_moves(x, y, gameboard, **kwargs)
                        | Rook(self.color).available_moves(x, y, gameboard, **kwargs)
                        | leaper(x, y, gameboard, self.color, dir8(1, 1), size=kwargs['size']))
    return self.tmp_moves
