import sys

import pygame
import pygame.event
from typing import Tuple

from dict_config import game
import dict_utils as dcu
import draw_utils as du
import pieces.piece_utils as pu
import utils

MousePos = Tuple[int, int]


def _select_initial_mouse_event(mousepos: MousePos):
  # 駒の頭文字の選択
  for i in range(26):
    if du.on_button(mousepos, (20 + (i // 9) * 320, 120 + 90 * (i % 9)), (140, 60)):
      game.initial = chr(i + 65)
      if dcu.pieces[game.initial]:
        game.piece = dcu.pieces[game.initial][0]
      game.select_initial = False
      game.select_piece = True
      game.top = 0
      return
  # Notation
  if du.on_button(mousepos, (20 + 640, 120 + 720), (140, 60)):
    game.select_initial = False
    game.notation_manual = True
    return


def _select_pieces_mouse_event(mousepos: MousePos):
  piece_num = len(dcu.pieces[game.initial])
  stop = game.top + 10 if game.top + 10 < piece_num else piece_num
  # 駒選択
  for i in range(game.top, stop):
    if du.on_button(mousepos, (60, 10 + 80 * (i + 1 - game.top)), (300, 80)):
      game.piece = dcu.pieces[game.initial][i]
      return
  # もどる
  if dcu.on_back_button(mousepos):
    game.select_piece = False
    game.select_initial = True
    return
  # 上へ
  if du.on_button(mousepos, (150, 50), (60, 20)):
    game.top -= 1 if game.top > 0 else 0
    return
  # 下へ
  if du.on_button(mousepos, (150, 910), (60, 20)):
    game.top += 1 if game.top + 10 < len(dcu.pieces[game.initial]) else 0
    return
  # 動かしてみる
  if du.on_button(mousepos, (830, 780), (50, 50)):
    game.select_piece = False
    game.place_pieces()
    return


def _select_pieces_key_event(key: int):
  _initial_list = dcu.pieces[game.initial]
  # [k] 上へ / [j] 下へ 選択移動
  if _initial_list:
    assert game.piece is not None
    _piece_index = _initial_list.index(game.piece)
    if key == pygame.K_k:
      _index = (_piece_index - 1) if _piece_index > 0 else 0
      game.top -= 1 if game.top > _index else 0
      game.piece = _initial_list[_index]
      return
    if key == pygame.K_j:
      _index = (_piece_index + 1) if _piece_index < len(_initial_list) - 1 else len(_initial_list) - 1
      game.top += 1 if game.top + 10 <= _index else 0
      game.piece = _initial_list[_index]
      return
  # [↑] 上へ / [↓] 下へ スクロール
  if key == pygame.K_UP:
    game.top -= 1 if game.top > 0 else 0
    return
  if key == pygame.K_DOWN:
    game.top += 1 if game.top + 10 < len(_initial_list) else 0
    return
  # [enter] 動かしてみる
  if key == pygame.K_RETURN:
    game.select_piece = False
    game.place_pieces()
    return
  # [backspace] もどる
  if key == pygame.K_BACKSPACE:
    game.select_piece = False
    game.select_initial = True
    return


def _archer_attack_mouse_event(mousepos: MousePos):
  _pos = du.parse_mouse(mousepos, game.kind['size'])
  if _pos in game.arrow_targets:
    if game.gameboard[_pos].color == 'B':
      del game.gameboard[_pos]
    game.shooting_target = _pos
    game.time = 0


def _move_pieces_mouse_event(mousepos: MousePos):
  _pointing_coord = du.parse_mouse(mousepos, game.kind['size'])
  _start = game.startpos
  _board = game.gameboard
  # 駒を移動させる
  # 先にこちらを書かないと駒を取れなくなる
  if _start is not None:
    _piece = _board[_start]
    if _pointing_coord in game.valid_moves(_piece, _start, _board):
      game.endpos = _pointing_coord
      game.time = 0
      game.moving = True
      # アーチャー系駒の攻撃が発生する条件
      # アーチャー系駒であることを示す属性が存在する
      # 移動で取ったときには矢は撃てない
      if hasattr(_piece, 'archer_dir') and game.endpos not in _board:
        game.arrow_targets = utils.arrow_targets_(_piece, _start, game.endpos, _board, pu.rider)
        if game.arrow_targets:
          # 自分の位置にも表示し、矢を打たないというオプションとする
          game.arrow_targets.add(game.endpos)
      game.main()
      return
  # 動かす駒を選択する
  if _pointing_coord in _board:
    game.startpos, game.endpos = _pointing_coord, None


def _pieces_action_mouse_event(mousepos: MousePos):
  # アーチャーの発射
  if game.arrow_targets:
    _archer_attack_mouse_event(mousepos)
  # 駒を移動させる
  else:
    _move_pieces_mouse_event(mousepos)
  # もどる
  if dcu.on_back_button(mousepos):
    game.startpos, game.endpos = None, None
    game.select_piece = True


def _mouse_event(pos: MousePos, button: int):
  '''マウス'''
  # 左
  if button == 1:
    # 初期画面
    if game.select_initial:
      _select_initial_mouse_event(pos)
    # 表記法説明
    elif game.notation_manual:
      # もどる
      if dcu.on_back_button(pos):
        game.notation_manual = False
        game.select_initial = True
    # 駒選択
    elif game.select_piece:
      _select_pieces_mouse_event(pos)
    # 盤面上で駒を動かす
    else:
      _pieces_action_mouse_event(pos)
  # 右
  elif (button == 3 and not game.select_initial
          and not game.notation_manual and not game.select_piece):
    # 駒選択解除
    game.startpos, game.endpos = None, None


def _key_event(key: int):
  if key == pygame.K_ESCAPE:
    pygame.quit()
    sys.exit()
  # 初期画面
  if game.select_initial:
    # [a-z] 該当の頭文字の駒一覧へ
    if ord('a') <= key <= ord('z'):
      game.initial = chr(key - 32)
      if dcu.pieces[game.initial]:
        game.piece = dcu.pieces[game.initial][0]
      game.select_initial = False
      game.select_piece = True
      game.top = 0
  elif game.notation_manual:
    # [backspace] もどる
    if key == pygame.K_BACKSPACE:
      game.notation_manual = False
      game.select_initial = True
  # 駒選択
  elif game.select_piece:
    _select_pieces_key_event(key)
  # 盤面上で駒を動かす
  else:
    # [backspace] もどる
    if key == pygame.K_BACKSPACE:
      game.startpos, game.endpos = None, None
      game.select_piece = True


def event():
  '''イベントハンドリング'''
  for event in pygame.event.get():
    # 閉じるボタン
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    # マウスクリック
    if (event.type == pygame.MOUSEBUTTONDOWN
        and not game.moving
            and game.shooting_target is None):
      _mouse_event(event.pos, event.button)
    # キーボード
    elif event.type == pygame.KEYDOWN:
      _key_event(event.key)
