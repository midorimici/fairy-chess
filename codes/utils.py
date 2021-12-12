'''処理に関する共通の関数を集めたモジュール'''

from copy import copy
from datetime import datetime
from typing import Tuple, Callable, Literal, cast

from custom_types import Color, Position, PositionList, PositionSet, Board, Placers
import numpy as np
import yaml

from pieces.piece import Piece


class CustomDumper(yaml.Dumper):
  def ignore_aliases(self, data):
    return True

  def increase_indent(self, flow=False, indentless=False):
    return super(CustomDumper, self).increase_indent(flow, False)


def save_print(draw, error: bool = False):
  '''
  現在のデータを記録する

  Parameters
  ----------
  draw : obj
    play.py で生成される draw = Draw() オブジェクト
  error : bool
    エラーとして出力

  Usus
  ----
  interact / Draw / handle_exc, keyboard
  '''
  def board_output(board: Board):
    return [{
            'position': pos,
            'name': type(piece).__name__,
            'color': piece.color,
            'count': getattr(piece, 'count', None),
            } for pos, piece in board.items()]

  data = [{
          'pick': False,
          'game_name_data': draw.kind['name'],
          'mode_data': draw.mode,
          'level_data': draw.level,
          'foreseeing_data': draw.foreseeing,
          'gameboard_data': board_output(draw.gameboard),
          'playersturn_data': draw.playersturn,
          'move_record_data': draw.move_record,
          'advanced2_pos_data': draw.advanced2_pos,
          'advanced2_record_data': draw.advanced2_record,
          'can_castling_data': draw.can_castling,
          'count_data': draw.count,
          'record_data': {
              number: board_output(board) for number, board in draw.record.items()
          },
          }]

  with open('main/data.yml', 'a') as file:
    file.write(f"# {'ERROR' if error else 'SAVE'}\n")
    file.write(f'# {datetime.now()}\n')
    yaml.dump(data, file, Dumper=CustomDumper, default_flow_style=None, sort_keys=False)
    print('✅ Data saved successfully!')


def value(color: Color, gameboard: Board):
  '''
  盤面上の双方の駒の価値の合計を出力する．
  King は除く．

  Parameters
  ----------
  color : Color
    駒色．
  gameboard : Board
    盤面．

  Returns
  -------
  : float
  '''
  return round(sum([piece.value
                    for piece in list(gameboard.values())
                    if piece.color == color and piece.abbr != 'K']), 1)


def pawn_init_pos(placers, size: int, asym: bool = False):
  '''
  ポーンの位置を辞書として出力する

  Parameters
  ----------
  placers : dict > {int: [obj, ...], ...}
    駒の配置．
  size : int
    盤面の大きさ．
  asym : bool
    非対称ゲームかどうか．

  Returns
  -------
  : dict > {'W': [(int, int), ...], 'B': ...}
  '''
  if asym:
    return {'W': [(file_, rank - 1)
                  for rank in placers
                  for file_, pc in enumerate(placers[rank])
                  if getattr(pc[0], 'abbr', None) == 'P'
                  and pc[1] == 'W'],
            'B': [(file_, rank - 1)
                  for rank in placers
                  for file_, pc in enumerate(placers[rank])
                  if getattr(pc[0], 'abbr', None) == 'P'
                  and pc[1] == 'B']}
  else:
    return {'W': [(file_, rank - 1)
                  for rank in placers
                  for file_, pc in enumerate(placers[rank])
                  if getattr(pc, 'abbr', None) == 'P'],
            'B': [(file_, size - rank)
                  for rank in placers
                  for file_, pc in enumerate(placers[rank])
                  if getattr(pc, 'abbr', None) == 'P']}


def rook_init_pos(placers: Placers):
  '''
  ルークの初期位置の x 座標

  Parameters
  ----------
  placers : dict > {int: (Piece | None, ...), ...}
    駒の配置．

  Returns
  -------
  (左側の x 座標, 右側の x 座標)
  (int, int)
  '''
  return cast(
      Tuple[int, int],
      tuple(pos for pos, piece in enumerate(placers[1]) if piece and piece.abbr == 'R'),
  )


def king_init_pos(placers: Placers):
  '''
  キングの初期位置の x 座標

  placers : dict > {int: (Piece | None, ...), ...}
    駒の配置．
  '''
  return next(pos for pos, piece in enumerate(placers[1]) if piece and piece.abbr == 'K')


def _castling_rook_route(init_pos: Tuple[int, int], size: int):
  '''キャスリング時にルークが通過するマス'''
  return [list(range(3, init_pos[0], -1 if init_pos[0] < 3 else 1)),
          list(range(size - 3, init_pos[1], -1 if init_pos[1] < size - 3 else 1))]


def castling_king_route(init_pos: int, size: int):
  '''キャスリング時にキングが通過するマス'''
  return [list(range(2, init_pos, -1 if init_pos < 2 else 1)),
          list(range(size - 2, init_pos, -1 if init_pos < size - 2 else 1))]


def castling_passable(
    placers: Placers,
    size: int,
    color: Color,
    side: Literal[0, 1],
    gameboard: Board,
):
  '''
  キングとルークの通過するマスに駒がないとき True
  (ただしキャスリングに関与するキングやルークは存在してもよい)

  Parameters
  ----------
  placers : dict > {int: (Piece | None, ...), ...}
    駒の配置．
  size : int
    盤面の大きさ．
  color : Color
    駒色．
  side : int > 0, 1
    0 -- クイーンサイド
    1 -- キングサイド
  gameboard : Board
    盤面．

  Returns
  -------
  bool
  '''
  _king_init_pos = king_init_pos(placers)
  _rook_init_pos = rook_init_pos(placers)
  gameboard_tmp = copy(gameboard)
  for pos in list(gameboard_tmp):
    if pos in [(_king_init_pos, 0 if color == 'W' else size - 1),
               (_rook_init_pos[side], 0 if color == 'W' else size - 1)]:
      # キャスリングに関与するキング・ルークの除外
      del gameboard_tmp[pos]
  return not any([(pos, 0 if color == 'W' else size - 1) in gameboard_tmp
                  for pos in _castling_rook_route(_rook_init_pos, size)[side]]
                 + [(pos, 0 if color == 'W' else size - 1) in gameboard_tmp
                     for pos in castling_king_route(_king_init_pos, size)[side]])


def create_tmp_board(gameboard: Board, start: Position, endpos: Position):
  '''
  キングの通過するマスが攻撃されていないことを確認するために，
  キングがそのマスに動いたときに攻撃されるかを見るための
  仮の盤面を出力する

  Parameters
  ----------
  gameboard : Board
  start : Position
    開始位置座標．
  endpos : Position
    終了位置．絶対座標．

  Returns
  -------
  gameboard_tmp : Board
  '''
  gameboard_tmp = copy(gameboard)
  if start in gameboard_tmp:
    gameboard_tmp[endpos] = gameboard_tmp[start]
    del gameboard_tmp[start]
  return gameboard_tmp


def move_list(pos: Position, arr: PositionSet) -> PositionSet:
  '''
  2列の行列posとarrの足し算
  posは二要素からなるタプル(x, y)
  arrを(x, y)平行移動
  arr(原点を駒とするときの動き，相対座標)を(x, y)を駒とするときの動き(絶対座標)に変換する

  Parameters
  ----------
  pos : Position
    駒の絶対座標．
  arr : PositionSet
    移動の方向の set

  Returns
  -------
  : PositionSet
    移動先(絶対座標)の set
  '''
  return {(xx, yy) for xx, yy in ([pos] + np.asarray(list(arr))).tolist()}


def advance_dir(startpos: Position, endpos: Position):
  '''
  startpos から endpos への進行方向を返す．-3~4．0 が前で反時計回り．

  1  0  -1
  2  Λ  -2
  3  4  -3

  Parameters
  ----------
  startpos, endpos : Position
    開始位置、終了位置．

  Returns
  -------
  int
    進行方向．
  '''
  ans: int = 0
  if endpos[0] == startpos[0]:
    if endpos[1] - startpos[1] > 0:
      ans = 0
    else:
      ans = 4
  elif (endpos[1] - startpos[1]) / (endpos[0] - startpos[0]) == 1:
    if endpos[1] - startpos[1] > 0:
      ans = -1
    else:
      ans = 3
  elif (endpos[1] - startpos[1]) / (endpos[0] - startpos[0]) == 0:
    if endpos[0] - startpos[0] > 0:
      ans = -2
    else:
      ans = 2
  elif (endpos[1] - startpos[1]) / (endpos[0] - startpos[0]) == -1:
    if endpos[1] - startpos[1] < 0:
      ans = -3
    else:
      ans = 1
  return ans


def dir2coord(dirs: 'list[int]') -> PositionList:
  '''
  アーチャー用．-3~4 の方向を座標表示に変換する．

  Parameters
  ----------
  dirs : list > [int, ...]
    方向のリスト．0 が前で時計回り．

  Returns
  -------
  answer : PositionList
    座標ベクトルのリスト．
  '''
  answer: PositionList = []

  for num in dirs:
    if num % 8 == 0:
      answer.append((0, 1))
    elif num % 8 == 1:
      answer.append((-1, 1))
    elif num % 8 == 2:
      answer.append((-1, 0))
    elif num % 8 == 3:
      answer.append((-1, -1))
    elif num % 8 == 4:
      answer.append((0, -1))
    elif num % 8 == 5:
      answer.append((1, -1))
    elif num % 8 == 6:
      answer.append((1, 0))
    elif num % 8 == 7:
      answer.append((1, 1))

  return answer


def arrow_targets_(
    piece: Piece, startpos: Position, endpos: Position, gameboard: Board,
    rider: Callable[[int, int, Board, Color, PositionList], PositionSet],
) -> PositionSet:
  '''
  piece が startpos -> endpos と動いたときに矢で攻撃できる位置 set を返す．

  Parameters
  ----------
  piece : Piece
    アーチャー系駒．
  startpos, endpos : Position
    開始位置，終了位置．
  gameboard : Board
    盤面．
  rider : func
    関数 rider()

  Returns
  -------
  PositionSet
  '''
  return {pos for pos in rider(*endpos, gameboard, piece.color,
                               dir2coord([num + advance_dir(startpos, endpos) for num in piece.archer_dir]))
          if pos in gameboard}


def in_zone(gameboard: Board, distance: int, position: Position, ref_piece_abbr: str):
  '''position が盤面上の ref_piece から
  distance マス以内にあるとき，True
  ただし position_piece == ref_piece のときは False

  Parameters
  ----------
  gameboard : Board
    盤面．
  distance : int > 1-
    範囲．1 のとき，隣のマス．
  position : Position
    位置．
  ref_piece_abbr : str
    基準となる駒の略称．

  Returns
  -------
  : bool
  '''
  ref_piece_positions = [pos
                         for pos, piece in gameboard.items() if piece.abbr == ref_piece_abbr]
  for ref_piece_position in ref_piece_positions:
    if (ref_piece_position[0] - distance <= position[0]
        <= ref_piece_position[0] + distance
        and ref_piece_position[1] - distance <= position[1]
            <= ref_piece_position[1] + distance):
      return True


def _memo():
  loaded = None
  args_memo = ()

  def f(func, *args):
    nonlocal loaded, args_memo
    if loaded is not None and args_memo == args:
      return loaded

    loaded = func(*args)
    args_memo = args
    return loaded
  return f


memo = _memo()
