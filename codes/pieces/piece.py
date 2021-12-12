'''すべての駒に共通するクラス Piece の定義'''

from copy import copy
from typing import Tuple, List, Set, Literal, Optional

Position = Tuple[int, int]
PositionList = List[Position]
PositionSet = Set[Position]


class Piece:
  '''すべての駒に共通のクラス

  Attributes
  ----------
  color : str > 'W', 'B'
    駒色．
  name : str
    駒色の後ろに駒の略記を付け加えたもの．
    WQ, BN など．
  moves : [(int, int)] = None
    実際の動き
  recalc : bool
    動きを再計算するか

  Notes
  -----
  すべての駒は，クラスにより定義されており，
  そのすべてが abbr, value 属性と，available_moves メソッドをもつ．

  Attributes
  ----------
  abbr : str
    駒の略記．
  value : float
    駒の価値．

  Methods
  -------
  available_moves(self, x, y, gameboard, **kwargs)

  Parameters
  ----------
  x, y : int
    駒の位置．絶対座標．
  gameboard : dict > {(int, int): obj, ...}
    盤面．
  count? : int
    その駒を動かした回数．

  Returns
  -------
  : PositionSet
    可能な移動先の座標の set．
  '''
  abbr: str
  value: float
  count: int
  archer_dir: 'list[int]'

  def __init__(self, color):
    self.color: Literal['W', 'B'] = color
    self.name: str = self.__repr__()
    self.moves: Optional[PositionList] = None
    self.recalc: bool = True
    self.seen_board = {}
    self.tmp_moves: PositionSet = set()

  def __repr__(self):
    return self.color + self.abbr

  def __str__(self):
    return self.color + self.abbr

  def prune(self, gameboard: 'dict[Position, Piece]', func, args) -> PositionSet:
    if gameboard != self.seen_board:
      self.seen_board = copy(gameboard)
      self.tmp_moves: PositionSet = func(*args)
    return self.tmp_moves

  def available_moves(self, x: int, y: int, gameboard: 'dict[Position, Piece]', **kwargs) -> PositionSet:
    return set()
