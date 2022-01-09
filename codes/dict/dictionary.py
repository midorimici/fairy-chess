'''駒の動きを学ぶためのプログラム'''


from typing import Type, Optional

from custom_types import Position, PositionSet, Board
from pieces.pieces import Piece, King
from pieces.fairy_pieces1 import Custom
import pieces.piece_utils as pu
import utils


class Game:
  def __init__(self):
    # ゲームの種類
    self.kind = {
        'size': 12,
        'placers': {
            1: (Custom,) + (None,) * 10 + (Custom,),
            3: (None,) * 2 + (Custom,) + (None,) * 6 + (Custom,) + (None,) * 2,
        },
    }
    # 盤面
    self.gameboard: Board = {}
    # 頭文字選択
    self.select_initial = True
    # 表記法説明
    self.notation_manual = False
    # 駒選択
    self.select_piece = False
    # 駒
    self.piece: Optional[Type[Piece]] = None
    # 頭文字
    self.initial: str
    # 最上に表示されている駒の番号
    self.top = 0

    # アニメーション
    self.moving = False
    self.shooting_target: Optional[Position] = None
    self.time = 0
    # 始点・終点
    self.startpos: Optional[Position] = None
    self.endpos: Optional[Position] = None

    # アーチャーの矢の可能な攻撃対象 : PositionSet
    self.arrow_targets: PositionSet = set()

  def place_pieces(self):
    '''駒を盤面に配置する'''
    self.gameboard = {}
    for fl in range(self.kind['size']):
      for rk in self.kind['placers']:
        _piece = self.kind['placers'][rk][fl]
        if _piece is not None:
          self.gameboard[(fl, rk - 1)] = _piece('W')
          self.gameboard[(fl, self.kind['size'] - rk)] = _piece('B')
    assert self.piece is not None
    self.gameboard[(self.kind['size'] // 2, self.kind['size'] // 2)] = self.piece('W')
    self.init_pos = (self.kind['size'] / 2, self.kind['size'] / 2)

  def main(self):
    '''盤面の状態の変更'''
    startpos, endpos = self.startpos, self.endpos
    if startpos is None or endpos is None:
      return

    target = self.gameboard.get(startpos)
    if target is None:
      return

    # 駒を動かした回数によって動きが変わる駒が動いた
    if hasattr(target, 'count'):
      target.count += 1
    # 通常の動き
    self.renew_gameboard(startpos, endpos, self.gameboard)

  def valid_moves(self, piece: Piece, startpos: Position, gameboard: Board) -> PositionSet:
    '''
    動ける位置を出力．味方駒上には移動不可．

    Parameters
    ----------
    piece : obj
        駒．
    startpos : tuple > (int, int)
        開始位置．絶対座標．
    gameboard : dict > {(int, int): obj, ...}
        盤面．

    Returns
    -------
    : list > [(int, int), ...]
    '''
    if utils.in_zone(gameboard, 1, startpos, 'Bz') and piece.abbr not in ('Mi', 'Bz'):
        # ブリザード範囲内
      result: PositionSet = set()
    elif utils.in_zone(gameboard, 2, startpos, 'Mi') and piece.abbr not in ('Mi', 'Bz'):
      # ミスト範囲内
      result = (King('W').available_moves(*startpos, gameboard, size=self.kind['size'])
                if piece.color == 'W'
                else King('B').available_moves(*startpos, gameboard, size=self.kind['size']))
    else:
      # 動く回数によって動きが変わる駒
      result = piece.available_moves(
          *startpos, gameboard, size=self.kind['size'])
    # 盤面の中に収まらなければならない
    result = {pos for pos in result if pu.is_in_bounds(*pos, self.kind['size'])}
    return result

  def renew_gameboard(self, startpos: Position, endpos: Position, gameboard: Board):
    '''盤面の更新

    Parameters
    ----------
    startpos, endpos : tuple > (int, int)
        開始位置，終了位置．絶対座標．
    gameboard : dict > {(int, int): obj, ...}
        盤面．
    color : str > 'W', 'B'
        駒色．
    '''
    # 通常の動き
    gameboard[endpos] = gameboard[startpos]
    if startpos != endpos:
      del gameboard[startpos]
