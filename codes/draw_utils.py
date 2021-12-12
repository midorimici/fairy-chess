'''描画に関する共通の関数を集めたモジュール'''


from math import pi, sin
import numpy as np
import pygame.draw
import pygame.font
import pygame.image
import pygame.math
import pygame.rect
import pygame.surface
import pygame.transform
from typing import Optional, Tuple, Literal

from config import (WSIZE, FONT_EN_16, FONT_EN_24, FONT_EN_32,
                    AMBER, BLACK, CORAL, LIGHTGREEN, INK, IVORY, ORANGE, WISTARIA, WHITE)
from custom_types import Position, PositionSet, Board, Piece


RGB = Tuple[int, int, int]


# サイズ計算

def square_size(board_size: int):
  '''
  盤面のマスのサイズを返す

  board_size : int
    盤面のサイズ（一列のマスの数）
  '''
  return WSIZE / (board_size + 1)


def resize(x: int, y: int):
  '''960x960 としたときの座標を実際のウィンドウサイズに合わせて変換する'''
  return x * WSIZE / 960, y * WSIZE / 960


def to_win_coord(coord: Tuple[float, float], board_size: int):
  '''
  盤面座標をウィンドウ座標に変換する

  Parameters
  ----------
  coord : Tuple[float, float]
    変換元の座標
  board_size : int
    盤面の大きさ

  Notes
  -----
  盤面座標
  n = board_size-1

     0       n
    ┌─┬     ┬─┐
  n │ │ ... │ │
    ├─┼     ┼─┤
    ...
    ├─┼     ┼─┤
  0 │ │ ... │ │
    └─┴     ┴─┘

  ウィンドウ座標
  sq_size = WSIZE/(board_size+1)

              sq_size  (n+1)*sq_size
                ┌─┬     ┬─┐
  sq_size       │ │ ... │ │
                ├─┼     ┼─┤
                    ...
                ├─┼     ┼─┤
  (n+1)*sq_size │ │ ... │ │
                └─┴     ┴─┘
  '''
  sq_size = square_size(board_size)
  x, y = coord
  return (x + 1) * sq_size, (board_size - y) * sq_size


# 画像関連

def _get_img():
  loaded = {}

  def f(path: str) -> pygame.surface.Surface:
    nonlocal loaded
    if loaded.get(path) is not None:
      return loaded[path]

    loaded[path] = pygame.image.load(f'../assets/img/{path}.png')
    return loaded[path]
  return f


get_img = _get_img()


# インタラクション関係

def parse_mouse(mousepos: Tuple[int, int], board_size: int, is_black: bool = False) -> Optional[Position]:
  '''
  マウスポインタの位置から指定したマス目を出力

  Parameters
  ----------
  mousepos : Tuple[int, int]
    マウスの座標
  board_size : int
    盤面のサイズ
  is_black : bool, default False
    黒のとき、見えている位置とは対称の位置を出力

  Returns
  -------
  : tuple > (float, float)
  '''
  sq_size = square_size(board_size)
  x, y = mousepos
  for i in range(board_size):
    wx = to_win_coord((i, 0), board_size)[0]
    if wx - sq_size / 2 < x < wx + sq_size / 2:
      fl = i
      break
  else:
    return None
  for i in range(board_size):
    wy = to_win_coord((0, i), board_size)[1]
    if wy - sq_size / 2 < y < wy + sq_size / 2:
      rk = i
      break
  else:
    return None
  if is_black:
    return (board_size - 1 - fl, board_size - 1 - rk)
  return (fl, rk)


def on_button(mouse_pos: 'tuple[int, int]', button_pos: 'tuple[int, int]', button_size: 'tuple[int, int]'):
  button_pos_np = np.asarray(resize(*button_pos))
  return np.all((button_pos_np <= resize(*mouse_pos),
                 resize(*mouse_pos) <= button_pos_np + resize(*button_size)))


# 基本図形

def draw_triangle(
    screen: pygame.surface.Surface,
    color: RGB,
    direction: Literal['U', 'R', 'D', 'L'],
    pos: Tuple[float, float],
):
  '''
  大きさ 40x30/960 の 三角を描画する

  Parameters
  ----------
  screen : Surface
  color : Tuple[int, int, int]
    色．(R, G, B) で指定．
  direction : 'U' | 'R' | 'D' | 'L'
    三角の向かう先の方向．
    'U' -- 上
    'R' -- 右
    'D' -- 下
    'L' -- 左
  pos : Tuple[float, float]
    先端の座標．
  '''
  p1 = (-20, -30)
  p2 = (20, -30)
  if direction == 'R':
    p1, p2 = (-30, 20), (-30, -20)
  elif direction == 'D':
    p1, p2 = (20, 30), (-20, 30)
  elif direction == 'L':
    p1, p2 = (30, -20), (30, 20)
  p0 = np.asarray((0, 0)) + pos
  p1 = np.asarray(p1) + pos
  p2 = np.asarray(p2) + pos
  pygame.draw.polygon(screen, color, (resize(*p0), resize(*p1), resize(*p2)))


def _arrow(angle: int, sq_size: int):
  '''
  矢印

  Parameters
  ----------
  angle : int > -180 - 180
    三角の向かう先の方向．0 が上で反時計回り．
  sq_size : int
    盤面のマスのサイズ
  '''
  surf = pygame.surface.Surface((sq_size, sq_size))
  surf.set_colorkey(BLACK)
  pygame.draw.line(surf, INK, (sq_size / 2, 0), (sq_size / 2, sq_size), width=2)
  points = (sq_size / 2, 0), (sq_size * 3 / 8, sq_size / 4), (sq_size * 5 / 8, sq_size / 4)
  pygame.draw.polygon(surf, INK, points)
  surf = pygame.transform.rotate(surf, angle)
  if angle % 90:
    cropped = pygame.surface.Surface((sq_size, sq_size))
    cropped.set_colorkey(BLACK)
    width = surf.get_width()
    pos = -(width - sq_size) / 2, -(width - sq_size) / 2
    cropped.blit(surf, pos)
    return cropped
  return surf


def draw_square(
    screen: pygame.surface.Surface, board_size: int, pos: Position, color: RGB,
):
  '''
  正方形を描画する

  Parameters
  ----------
  screen : Surface
  board_size : int
    盤面のサイズ
  pos : Position
    中心の座標．盤面座標．
  color : Tuple[int, int, int]
    色
  '''
  sq_size = square_size(board_size)
  left_top: tuple[float] = tuple(np.asarray(to_win_coord(pos, board_size)) - sq_size / 2)
  rect = pygame.rect.Rect(left_top, (sq_size, sq_size))
  pygame.draw.rect(screen, color, rect)


def _draw_circles(
    screen: pygame.surface.Surface, board_size: int, pos_set: PositionSet, color: RGB,
    is_black: bool = False,
):
  '''
  半透明の円を描画する

  screen : Surface
  board_size : int
    盤面のサイズ
  pos_set : PositionSet
    描画する位置 set
  color : Tuple[int, int, int]
    円の色
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  sq_size = square_size(board_size)
  surf = pygame.surface.Surface((WSIZE, WSIZE))
  surf.set_colorkey(BLACK)
  surf.set_alpha(180)
  for pos in pos_set:
    if is_black:
      pos = (board_size - 1 - pos[0], board_size - 1 - pos[1])
    pygame.draw.circle(surf, color, to_win_coord(pos, board_size), sq_size / 4)
  screen.blit(surf, (0, 0))

# 図形描画


def draw_button(
    screen: pygame.surface.Surface,
    text: str,
    coord: Tuple[float, float],
    size: Tuple[float, float],
    color: RGB = AMBER,
    bgcolor: RGB = IVORY,
    font: pygame.font.Font = FONT_EN_32,
):
  '''
  ボタンを描画する

  screen : Surface
  text : str
    中身のテキスト
  coord : Tuple[float, float]
    左上の座標
  size : Tuple[float, float]
    横、縦のサイズ
  color : tuple <- (0-255, 0-255, 0-255)
    文字色
  bgcolor : tuple <- (0-255, 0-255, 0-255)
    背景色
  font : Font
    フォント
  '''
  rect = pygame.rect.Rect(coord, size)
  pygame.draw.rect(screen, bgcolor, rect, border_radius=8)
  rendered_text = font.render(text, True, color)
  fsize = np.asarray(font.size(text))
  screen.blit(rendered_text, list(coord + (size - fsize) / 2))

# ゲーム関連


def _dark_square_list(size: int):
  '''
  色が濃いマスの座標を出力

  Parameters
  ----------
  size : int
    盤面の大きさ．

  Returns
  -------
  : list > [(int, int), ...]
  '''
  return ([(i, j) for i in range(0, size, 2) for j in range(0, size, 2)]
          + [(i, j) for i in range(1, size, 2) for j in range(1, size, 2)])


def draw_squares(
    screen: pygame.surface.Surface,
    startpos: Optional[Position], selected: Optional[Position],
    size: int, is_black: bool = False,
):
  '''
  マス目を描画する

  Parameters
  ----------
  screen : Surface
  startpos : Position | None
    開始位置の座標．
  selected : Position | None
    キーボード選択中の位置
  size : int
    盤面の大きさ．
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  for i in range(size):
    for j in range(size):
      if (i, j) in _dark_square_list(size):
        draw_square(screen, size, (i, j), AMBER)
      else:
        draw_square(screen, size, (i, j), IVORY)
  # 開始位置のマスの色を変える．
  if startpos is not None:
    surf = pygame.surface.Surface((WSIZE, WSIZE))
    surf.set_colorkey(BLACK)
    surf.set_alpha(120)
    if is_black:
      startpos = (size - 1 - startpos[0], size - 1 - startpos[1])
    draw_square(surf, size, startpos, LIGHTGREEN)
    screen.blit(surf, (0, 0))
  # 選択中の位置のマスの色を変える
  if selected is not None:
    surf = pygame.surface.Surface((WSIZE, WSIZE))
    surf.set_colorkey(BLACK)
    surf.set_alpha(120)
    if is_black:
      selected = (size - 1 - selected[0], size - 1 - selected[1])
    draw_square(surf, size, selected, LIGHTGREEN)
    screen.blit(surf, (0, 0))


def draw_file(screen: pygame.surface.Surface, size: int = 8, is_black: bool = False):
  '''
  ファイルの文字を描画する

  Parematers
  ----------
  screen : Surface
  size : int, default 8
    盤面の大きさ．
  is_black : bool, default False
    True のとき，逆順にする
  '''
  for x in range(size):
    if is_black:
      text = chr(size - 1 - x + 97)
    else:
      text = chr(x + 97)
    screen.blit(
        FONT_EN_24.render(text, True, WHITE),
        to_win_coord((x, -0.5), size),
    )


def draw_rank(screen: pygame.surface.Surface, size: int = 8, is_black: bool = False):
  '''
  ランクの文字を描画する

  Parematers
  ----------
  screen : Surface
  size : int, default 8
    盤面の大きさ．
  is_black : bool, default False
    True のとき，逆順にする
  '''
  for y in range(size):
    if is_black:
      text = str(size - 1 - y + 1)
    else:
      text = str(y + 1)
    screen.blit(
        FONT_EN_24.render(text, True, WHITE),
        to_win_coord((-1, y + 0.25), size),
    )


def draw_piece(screen: pygame.surface.Surface, piece: Piece, pos: Tuple[float, float], sq_size: int):
  '''
  駒を単体で描画する

  Parematers
  ----------
  screen : Surface
  piece : Piece
    駒
  pos : Tuple[float, float]
    描画するウィンドウ座標
  sq_size : int
    盤面のマスのサイズ
  '''
  img = get_img(f'{piece.color}/{piece.name}')
  img = pygame.transform.smoothscale(img, (sq_size, sq_size))
  screen.blit(img, pos)
  # 一部の駒には移動回数も一緒に表示する
  if piece.abbr in ('DM', 'DM2', 'DP'):
    screen.blit(
        FONT_EN_16.render(str(piece.count), True, INK),
        tuple(np.asarray(pos) + sq_size * 3 / 4),
    )


def draw_pieces(
    screen: pygame.surface.Surface, gameboard: Board, size: int,
    hide: Optional[Position], is_black: bool = False,
):
  '''
  盤面上の駒を描画する

  Parematers
  ----------
  screen : Surface
  gameboard : Board
    盤面．
  size : int
    盤面の大きさ．
  hide : Position | None
    描画をスキップする駒の位置
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  sq_size = int(square_size(size))
  for i in range(size):
    for j in range(size):
      piece = gameboard.get((i, j))
      if piece is not None and hide != (i, j):
        left_top: tuple[float, float] = tuple(np.asarray(
            to_win_coord((size - 1 - i, size - 1 - j) if is_black else (i, j), size)) - sq_size / 2
        )
        draw_piece(screen, piece, left_top, sq_size)


def draw_board(
    screen: pygame.surface.Surface, start: Optional[Position], size: int, board: Board,
    hide: Optional[Position] = None, selected: Optional[Position] = None, is_black: bool = False,
):
  '''
  盤面を描画する

  screen : Surface
  start : Position | None
    駒の位置
  size : int
    盤面のサイズ
  board : Board
    盤面
  hide : Position | None
    描画をスキップする駒の位置
  selected : Position | None
    キーボード選択中の位置
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  draw_squares(screen, start, selected, size, is_black)
  draw_file(screen, size=size, is_black=is_black)
  draw_rank(screen, size=size, is_black=is_black)
  draw_pieces(screen, board, size, hide, is_black)


def draw_available_moves(
    screen: pygame.surface.Surface, board_size: int, pos_set: PositionSet,
    change_color_condition: bool = False, is_black: bool = False,
):
  '''
  動かせる位置を描画する

  Parameters
  ----------
  screen : Surface
  board_size : int
    盤面のサイズ
  pos_set : PositionSet
    移動先の座標の set．
  change_color_condition : bool, default False
    True のとき，赤色で描画する．
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  color = CORAL if change_color_condition else WISTARIA
  _draw_circles(screen, board_size, pos_set, color, is_black)


def draw_piece_anim(
    screen: pygame.surface.Surface, board_size: int, piece: Piece, start: Position, end: Position,
    time: int, is_black: bool = False,
):
  '''
  アニメーション中の駒を描画する

  screen : Surface
  board_size: int
    盤面のサイズ
  piece : Piece
    駒
  start : Position
    駒の移動元の盤面座標
  end : Position
    駒の移動先の盤面座標
  time : int
    アニメーション開始からのコマ数
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  # 動き中の駒を描画する
  sq_size = int(square_size(board_size))
  s = pygame.math.Vector2(start)
  e = pygame.math.Vector2(end)
  pos = s + ((e - s) / 2) * (sin(pi * (time - 5) / 10) + 1)
  if is_black:
    _pos = (board_size - 1 - pos.x, board_size - 1 - pos.y)
  else:
    _pos = (pos.x, pos.y)
  left_top = pygame.math.Vector2(to_win_coord(_pos, board_size)).elementwise() - sq_size / 2
  draw_piece(screen, piece, (left_top.x, left_top.y), sq_size)


def draw_arrow_target(
    screen: pygame.surface.Surface, board_size: int, pos_set: PositionSet, is_black: bool = False
):
  '''
  矢で攻撃できる位置を描画する

  Parameters
  ----------
  screen : Surface
  board_size : int
    盤面のサイズ
  pos_set : PositionSet
    移動先の座標の set．
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  _draw_circles(screen, board_size, pos_set, ORANGE, is_black)


def draw_arrow_anim(
    screen: pygame.surface.Surface, board_size: int, angle: int, start: Position, end: Position,
    time: int, is_black: bool = False,
):
  '''
  アニメーション中の矢を描画する

  screen : Surface
  board_size: int
    盤面のサイズ
  angle : int > -180 - 180
    三角の向かう先の方向．0 が上で反時計回り．
  start : Position
    駒の移動元の盤面座標
  end : Position
    駒の移動先の盤面座標
  time : int
    アニメーション開始からのコマ数
  is_black : bool, default False
    True のとき，画面の中心に対して対称にする．
  '''
  sq_size = int(square_size(board_size))
  s = pygame.math.Vector2(start)
  e = pygame.math.Vector2(end)
  pos = s + (e - s) * time / 10
  if is_black:
    _pos = (board_size - 1 - pos.x, board_size - 1 - pos.y)
  else:
    _pos = (pos.x, pos.y)
  left_top = pygame.math.Vector2(to_win_coord(_pos, board_size)).elementwise() - sq_size / 2
  screen.blit(_arrow(angle + (180 if is_black else 0), sq_size), (int(left_top.x), int(left_top.y)))


def draw_cmd(screen: pygame.surface.Surface, repeat_num: Optional[str], dest: Optional[str]):
  '''
  キーボードコマンドを描画する

  screen : Surface
  repeat_num : str | None
    コマンド繰り返し数値
  dest : str | None
    移動先として指定されたマスを表すコマンド
  '''
  if repeat_num is not None:
    cmd = repeat_num
  elif dest is not None:
    cmd = f'g{dest}'
  else:
    return

  screen.blit(FONT_EN_16.render(cmd, True, WHITE), resize(910, 930))
