'''駒に関するクラスを集めたモジュール

Normal Chess の6つの駒の定義

Notes
-----
画像はこちらからお借りしています
https://www.1001freedownloads.com/free-clipart/chess-symbols-set-13
'''


from copy import copy

from pieces.piece import Piece, PositionSet
from pieces.piece_utils import dir8, king_move, leaper, no_conflict, rider


class Knight(Piece):
  abbr = 'N'
  value = 3.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color, dir8(1, 2), kwargs['size']))


class Rook(Piece):
  abbr = 'R'
  value = 5.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, rider,
                      (x, y, gameboard, self.color, dir8(0, 1), kwargs['size']))


class Bishop(Piece):
  abbr = 'B'
  value = 3.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, rider,
                      (x, y, gameboard, self.color, dir8(1, 1), kwargs['size']))


class Queen(Piece):
  abbr = 'Q'
  value = 9.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, rider,
                      (x, y, gameboard, self.color, king_move, kwargs['size']))


class King(Piece):
  abbr = 'K'
  value = 10.0

  def available_moves(self, x, y, gameboard, **kwargs):
    return self.prune(gameboard, leaper,
                      (x, y, gameboard, self.color, king_move, kwargs['size']))


class Pawn(Piece):
  abbr = 'P'
  value = 1.0

  def __init__(self, color):
    super().__init__(color)
    self.count = 0

  def available_moves(self, x, y, gameboard, **kwargs):
    _direction = 1 if self.color == 'W' else -1
    capture = ((x + 1, y + _direction), (x - 1, y + _direction))
    if kwargs.get('return_capture'):
      return capture

    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      move: PositionSet = set()
      if (x, y + _direction) not in gameboard:
        move.add((x, y + _direction))
      if (self.count == 0
              and (x, y + 1 * _direction) not in gameboard
              and (x, y + 2 * _direction) not in gameboard):
        move.add((x, y + 2 * _direction))
      self.tmp_moves = move | {pos for pos in capture
                               if (pos in gameboard and no_conflict(
                                   gameboard, self.color, *pos, size=kwargs['size']))}
    return self.tmp_moves
