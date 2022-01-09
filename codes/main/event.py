import sys

import pygame
import pygame.event
from typing import Optional, Tuple

from custom_types import Position
import draw_utils as du
import event_utils as eu
from games import games
from main_config import game, select_snd, play
import utils

MousePos = Tuple[int, int]


def _select_game_mouse_event(mpos: MousePos):
  '''ゲームの種類の選択'''
  base_index = 10 * (game.page - 1)
  for i in range(2):
    for j in range(5):
      index = base_index + 5 * i + j
      if (index < len(games)
              and du.on_button(mpos, (40 + 460 * i, 40 + 160 * j), (420, 120))):
        eu.decide_game_event(index)
        return
  total_pages = len(games) // 10 + 1
  # 前のページへ
  if du.on_button(mpos, (260, 860), (130, 40)):
    eu.prev_page_event(total_pages)
  # 次のページへ
  elif du.on_button(mpos, (570, 860), (130, 40)):
    eu.next_page_event(total_pages)


def _select_game_key_event(key: int):
  '''ゲームの種類の選択画面'''
  # [0-9] ゲームの種類の選択
  if ord('0') <= key <= ord('9'):
    index = 10 * (game.page - 1) + key - 48
    if (index < len(games)):
      eu.decide_game_event(index)
    return
  total_pages = len(games) // 10 + 1
  # [←] 前のページへ
  if key == pygame.K_LEFT:
    eu.prev_page_event(total_pages)
  # [→] 次のページへ
  elif key == pygame.K_RIGHT:
    eu.next_page_event(total_pages)


def _settings_mouse_event(mpos: MousePos):
  '''色・モードなどの設定'''
  # 色
  if du.on_button(mpos, (120, 270), (300, 120)) and game.my_color == 'B':
    eu.select_color_event('W')
  elif du.on_button(mpos, (540, 270), (300, 120)) and game.my_color == 'W':
    eu.select_color_event('B')
  # モード
  elif du.on_button(mpos, (120, 570), (300, 120)) and game.mode == 'PvsC':
    eu.select_mode_event('PvsP')
  elif du.on_button(mpos, (540, 570), (300, 120)) and game.mode == 'PvsP':
    eu.select_mode_event('PvsC')
  # レベル
  elif game.level:
    for i in range(1, 6):
      if du.on_button(mpos, (180 + 120 * i, 750), (64, 32)) and game.level != i:
        game.level = i
        play(select_snd)
        return
  # 先読みの有無
  if du.on_button(mpos, (300, 840), (40, 40)):
    eu.toggle_foreseeing_event()
  # もどる
  elif du.on_button(mpos, (30, 30), (210, 90)):
    eu.back_event()
  # 決定
  elif du.on_button(mpos, (720, 30), (210, 90)):
    eu.start_game_event()


def _settings_key_event(key: int):
  '''色・モードなどの設定'''
  # [w] / [b] 色
  if key == pygame.K_w and game.my_color == 'B':
    eu.select_color_event('W')
  elif key == pygame.K_b and game.my_color == 'W':
    eu.select_color_event('B')
  # [p] / [c] モード
  elif key == pygame.K_p and game.mode == 'PvsC':
    eu.select_mode_event('PvsP')
  elif key == pygame.K_c and game.mode == 'PvsP':
    eu.select_mode_event('PvsC')
  elif game.level:
    # [1-5] レベル
    if 49 <= key <= 53 and game.level != key - 48:
      game.level = key - 48
      play(select_snd)
      return
    # [f] 先読みの有無
    elif key == pygame.K_f:
      eu.toggle_foreseeing_event()
      return
  # [backspace] もどる
  if key == pygame.K_BACKSPACE:
    eu.back_event()
  # [enter] 決定
  elif key == pygame.K_RETURN:
    eu.start_game_event()


def _back_to_home_mouse_event(mpos: MousePos):
  '''ゲーム選択メニューに戻る'''
  # 戻る
  if du.on_button(mpos, (360, 480), (90, 60)):
    eu.back_to_home_event()
  # 戻らない
  elif du.on_button(mpos, (510, 480), (90, 60)):
    eu.cancel_back_to_home_event()


def _back_to_home_key_event(key: int):
  '''ゲーム選択メニューに戻る'''
  # [y] 戻る
  if key == pygame.K_y:
    eu.back_to_home_event()
  # [n] 戻らない
  elif key == pygame.K_n:
    eu.cancel_back_to_home_event()


def _pieces_action_mouse_event(mpos: MousePos):
  '''駒の動作'''
  assert game.kind is not None
  _pos = du.parse_mouse(mpos, game.kind['size'], game.my_color == 'B')
  # アーチャーの発射
  if game.arrow_targets:
    eu.archer_attack_event(_pos)
  # 駒を移動させる
  else:
    eu.move_pieces_event(_pos)


def _specify_destination_key_event(key: int):
  '''移動先のマスを指定'''
  # [g] コマンドの記録を開始
  if key == pygame.K_g and game.dest_cmd is None:
    game.show_value = False
    game.show_user_guide = False
    game.dest_cmd = ''
  # [a-l] ファイルを指定
  elif ord('a') <= key <= ord('l') and game.dest_cmd == '':
    game.dest_cmd += chr(key)
  # [0-9] ランクを指定
  elif ord('0') <= key <= ord('9') and game.dest_cmd is not None and len(game.dest_cmd) < 3:
    game.dest_cmd += chr(key)
  # [enter] 確定・選択
  elif key == pygame.K_RETURN and game.dest_cmd:
    assert game.kind is not None
    _size = game.kind['size']
    _current = game.selecting_square or (0, 0)
    # ファイル
    # 指定されていたらそれを使う
    if 0 <= ord(game.dest_cmd[0]) - 97 < _size:
      _file = ord(game.dest_cmd[0]) - 97
    # 指定されていなかったら現在のものを使う
    else:
      _file = _current[0]
    # ランク
    _num = int(''.join(c for c in game.dest_cmd if c.isdigit()) or 0)
    # 指定されていたらそれを使う
    if 1 <= _num <= _size:
      _rank = _num - 1
    # 指定されていなかったら現在のものを使う
    else:
      _rank = _current[1]
    game.selecting_square = (_file, _rank)
    game.dest_cmd = None


def _specify_repeat_key_event(key: int):
  '''コマンド繰り返し回数の指定'''
  # [0-9] コマンド繰り返し回数の指定
  if ord('0') <= key <= ord('9'):
    game.show_value = False
    game.show_user_guide = False
    if game.cmd_repeat_num is None:
      if key == ord('0'):
        return
      game.cmd_repeat_num = chr(key)
    elif len(game.cmd_repeat_num) < 2:
      game.cmd_repeat_num += chr(key)


def _nav_square_key_event(key: int, shift: int, sel_sq: Optional[Position], rep: int):
  '''左/下/上/右の（駒のある）マス、左上/右上/左下/右下のマスを選択'''
  assert game.kind is not None
  _size = game.kind['size']
  _revesed = game.my_color == 'B'

  # [h][j][k][l] 左/下/上/右のマスを選択
  # [H][J][K][L] 左/下/上/右の次の駒があるマスを選択
  # [e][r][d][f] 左上/右上/左下/右下のマスを選択
  if key not in (pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l,
                 pygame.K_e, pygame.K_r, pygame.K_d, pygame.K_f):
    return

  game.show_value = False
  game.show_user_guide = False
  game.cmd_repeat_num = None

  _left_key = pygame.K_l if _revesed else pygame.K_h
  _down_key = pygame.K_k if _revesed else pygame.K_j
  _up_key = pygame.K_j if _revesed else pygame.K_k
  _right_key = pygame.K_h if _revesed else pygame.K_l
  _lu_key = pygame.K_f if _revesed else pygame.K_e
  _ru_key = pygame.K_d if _revesed else pygame.K_r
  _ld_key = pygame.K_r if _revesed else pygame.K_d
  _rd_key = pygame.K_e if _revesed else pygame.K_f

  if sel_sq is None:
    game.selecting_square = game.startpos or (0, 0)
  elif key == _left_key and sel_sq[0] > 0:
    if shift:
      _x_list = sorted(x for x, y in game.gameboard if x < sel_sq[0] and y == sel_sq[1])
      if len(_x_list) > 0:
        _new_x = _x_list[-min(len(_x_list), rep)]
      else:
        return
    else:
      _new_x = max(0, sel_sq[0] - rep)
    game.selecting_square = _new_x, sel_sq[1]
  elif key == _down_key and sel_sq[1] > 0:
    if shift:
      _y_list = sorted(y for x, y in game.gameboard if x == sel_sq[0] and y < sel_sq[1])
      if len(_y_list) > 0:
        _new_y = _y_list[-min(len(_y_list), rep)]
      else:
        return
    else:
      _new_y = max(0, sel_sq[1] - rep)
    game.selecting_square = sel_sq[0], _new_y
  elif key == _up_key and sel_sq[1] < _size - 1:
    if shift:
      _y_list = sorted(y for x, y in game.gameboard if x == sel_sq[0] and y > sel_sq[1])
      if len(_y_list) > 0:
        _new_y = _y_list[min(len(_y_list), rep) - 1]
      else:
        return
    else:
      _new_y = min(_size - 1, sel_sq[1] + rep)
    game.selecting_square = sel_sq[0], _new_y
  elif key == _right_key and sel_sq[0] < _size - 1:
    if shift:
      _x_list = sorted(x for x, y in game.gameboard if x > sel_sq[0] and y == sel_sq[1])
      if len(_x_list) > 0:
        _new_x = _x_list[min(len(_x_list), rep) - 1]
      else:
        return
    else:
      _new_x = min(_size - 1, sel_sq[0] + rep)
    game.selecting_square = _new_x, sel_sq[1]
  elif key == _lu_key and sel_sq[0] > 0 and sel_sq[1] < _size - 1:
    game.selecting_square = max(0, sel_sq[0] - rep), min(_size - 1, sel_sq[1] + rep)
  elif key == _ru_key and sel_sq[0] < _size - 1 and sel_sq[1] < _size - 1:
    game.selecting_square = min(_size - 1, sel_sq[0] + rep), min(_size - 1, sel_sq[1] + rep)
  elif key == _ld_key and sel_sq[0] > 0 and sel_sq[1] > 0:
    game.selecting_square = max(0, sel_sq[0] - rep), max(0, sel_sq[1] - rep)
  elif key == _rd_key and sel_sq[0] < _size - 1 and sel_sq[1] > 0:
    game.selecting_square = min(_size - 1, sel_sq[0] + rep), max(0, sel_sq[1] - rep)


def _select_candidates_key_event(key: int, shift: int, sel_sq: Optional[Position], rep: int):
  '''行先・矢のターゲットの候補を選択'''
  # [n]/[N] 次/前の候補を選択
  if key != pygame.K_n:
    return

  game.show_value = False
  game.show_user_guide = False
  game.cmd_repeat_num = None
  _pos_candidates = None
  # 矢のターゲット
  if game.arrow_targets:
    _pos_candidates = sorted(game.arrow_targets)
  # 行先
  elif game.startpos is not None:
    _pos_candidates = game.valid_moves(game.gameboard[game.startpos], game.startpos)
  # 候補の選択
  if _pos_candidates is None:
    return

  if sel_sq in _pos_candidates:
    _new_index = (_pos_candidates.index(sel_sq) + (-rep if shift else rep)) % len(_pos_candidates)
  else:
    _new_index = -rep if shift else 0
  game.selecting_square = _pos_candidates[_new_index]


def _select_square_key_event(key: int, shift: int):
  '''位置の選択・駒の移動'''
  if game.cmd_repeat_num is None:
    _specify_destination_key_event(key)
  if game.dest_cmd is None:
    _sel_sq = game.selecting_square
    _rep = int(game.cmd_repeat_num or '1')
    _specify_repeat_key_event(key)
    _nav_square_key_event(key, shift, _sel_sq, _rep)
    _select_candidates_key_event(key, shift, _sel_sq, _rep)


def _pieces_action_key_event(key: int, shift: int):
  '''駒の動作'''
  # 選択を確定する
  if key == pygame.K_RETURN and game.dest_cmd is None:
    # アーチャーの発射
    if game.arrow_targets:
      eu.archer_attack_event(game.selecting_square)
    # 駒の移動
    else:
      eu.move_pieces_event(game.selecting_square)
    game.show_value = False
    game.show_user_guide = False
  # マスを選択する
  _select_square_key_event(key, shift)


def _promotion_mouse_event(mpos: MousePos):
  '''プロモーション先の選択'''
  if not game.prom:
    return

  assert game.kind is not None
  assert game.endpos is not None
  _num = len(game.kind['promote2'])
  _piece_size = int(du.square_size(game.kind['size']))
  _area_size = _piece_size + 30
  _rect_width = _area_size * (_num % 4 if _num < 4 else 4)
  _rect_height = _area_size * (1 + (_num - 1) // 4)
  _rect_left = 480 - _rect_width // 2
  _rect_top = 480 - _rect_height // 2
  for i in range(_num):
    if du.on_button(mpos, (
        _rect_left + _area_size * (i % 4),
        _rect_top + _area_size * (i // 4),
    ), (_area_size, _area_size)):
      eu.promotion_event(i)
      return


def _promotion_key_event(key: int):
  '''プロモーション先の選択'''
  assert game.kind is not None
  assert game.endpos is not None
  _index = game.selecting_prom_piece_index
  if game.selecting_prom_piece_index is None:
    game.selecting_prom_piece_index = 0
    return
  assert _index is not None
  _promote_len = len(game.kind['promote2'])
  if key == pygame.K_LEFT:
    game.selecting_prom_piece_index -= 0 if _index % 4 == 0 else 1
  elif key == pygame.K_UP:
    game.selecting_prom_piece_index -= 4 if _index // 4 > 0 else 0
  elif key == pygame.K_RIGHT:
    game.selecting_prom_piece_index += 0 if _index % 4 == 3 else 1
  elif key == pygame.K_DOWN:
    game.selecting_prom_piece_index += 4 if _index // 4 <= _promote_len // 4 else 0
  elif key == pygame.K_RETURN:
    eu.promotion_event(_index)
    return
  if game.selecting_prom_piece_index > _promote_len - 1:
    game.selecting_prom_piece_index = _promote_len - 1


def _castling_confirmation_mouse_event(mpos: MousePos):
  '''キャスリングするかどうかの確認'''
  if not game.confirm_castling:
    return

  # する
  _on_yes_button = du.on_button(mpos, (360, 480), (90, 60))
  _on_no_button = False
  if _on_yes_button:
    game.do_castling = True
  else:
    # しない
    _on_no_button = du.on_button(mpos, (510, 480), (90, 60))
    if _on_no_button:
      game.do_castling = False

  if _on_yes_button or _on_no_button:
    eu.castling_event()


def _castling_confirmation_key_event(key: int):
  '''キャスリングするかどうかの確認'''
  # [y] する
  if key == pygame.K_y:
    game.do_castling = True
  # [n] しない
  elif key == pygame.K_n:
    game.do_castling = False
  if key in (pygame.K_y, pygame.K_n):
    eu.castling_event()


def _board_back_forward_key_event(key: int):
  '''盤面を戻したり進めたりするキーボードイベント'''
  if game.prom or game.confirm_castling or game.moving or game.arrow_targets != set():
    return

  # [z] 一手戻す
  if key == pygame.K_z:
    game.prev_move()
    if game.mode == 'PvsC':
      game.prev_move()
  # [x] 一手進める
  elif key == pygame.K_x:
    game.next_move()


def _game_key_event(key: int, mod: int):
  '''ゲーム中のキーボードイベント'''
  # [y] / [n] ゲーム選択メニューに戻るかの確認の決定
  if game.alert:
    _back_to_home_key_event(key)
  # [y] / [n] キャスリングするかの確認の決定
  elif game.confirm_castling:
    _castling_confirmation_key_event(key)
  # [←][⇡][→][↓][enter] プロモーション先の選択・決定
  elif game.prom:
    _promotion_key_event(key)
  else:
    # 駒の移動・矢の射撃
    _pieces_action_key_event(key, mod & pygame.KMOD_SHIFT)
    # [space] 駒の説明を表示
    if key == pygame.K_SPACE and game.startpos is not None:
      game.piece_for_description = game.gameboard[game.startpos].__class__.__name__
      game.time = 0
      game.show_value = False
      game.show_user_guide = False
      return
    # [backspace] ゲーム選択メニューに戻るかの確認
    if key == pygame.K_BACKSPACE:
      game.alert = True
      game.show_value = False
      game.show_user_guide = False
      return
    # [v] 駒の価値を表示する
    if key == pygame.K_v:
      game.show_value = not game.show_value
      game.show_user_guide = False
      return
    # [shift+/]/[?] ヘルプを表示する
    if key == pygame.K_SLASH and mod & pygame.KMOD_SHIFT:
      game.show_user_guide = not game.show_user_guide
      game.show_value = False
      return
    # [ctrl+s] ゲームデータのセーブ
    if key == pygame.K_s and mod & pygame.KMOD_CTRL:
      print('Save the data:\nSet pick: true in one of the data saved in data.yml.')
      print('Then visit the same game again and type ctrl+L, or just run command with color option.\n')
      utils.save_print(game)
      return
    # [ctrl+l] ゲームデータのロード
    if key == pygame.K_l and mod & pygame.KMOD_CTRL:
      game.load_data()
      return
    # [z] / [x] 一手戻す / 進める
    _board_back_forward_key_event(key)


def _left_mouse_event(pos: MousePos):
  '''左クリックイベント'''
  # ゲームの種類の選択
  if game.select_game:
    _select_game_mouse_event(pos)
    return
  # 色・モードなどの設定
  elif game.select_color:
    _settings_mouse_event(pos)
    return

  # ゲーム
  if game.alert:
    _back_to_home_mouse_event(pos)
  elif not game.show_value and not game.show_user_guide:
    _pieces_action_mouse_event(pos)
    _promotion_mouse_event(pos)
    _castling_confirmation_mouse_event(pos)
  game.selecting_square = game.cmd_repeat_num = game.dest_cmd = None


def _right_mouse_event(pos: MousePos):
  '''右クリックイベント'''
  assert game.kind is not None
  _pointing_coord = du.parse_mouse(pos, game.kind['size'], game.my_color == 'B')
  if (_pointing_coord in game.gameboard
      and not game.alert
      and not game.show_value
          and not game.show_user_guide):
    # 駒の説明を表示
    assert _pointing_coord is not None
    game.piece_for_description = game.gameboard[_pointing_coord].__class__.__name__
    game.time = 0
  else:
    # 駒選択解除
    game.startpos, game.endpos = None, None


def _mouse_event(pos: MousePos, button: int):
  '''マウス'''
  # 左
  if button == 1:
    _left_mouse_event(pos)
  # 右
  elif (button == 3
        and not (game.select_game or game.select_color)
        and not game.prom
        and not game.confirm_castling):
    _right_mouse_event(pos)


def _key_event(key: int, mod: int):
  # 閉じる
  if key == pygame.K_ESCAPE:
    pygame.quit()
    sys.exit()
  # ゲームの種類の選択
  if game.select_game:
    _select_game_key_event(key)
  # 色・モードなどの設定
  elif game.select_color:
    _settings_key_event(key)
  # ゲーム中
  else:
    # 駒説明を非表示にする
    game.piece_for_description = None
    _game_key_event(key, mod)


def event():
  '''イベントハンドリング'''
  for event in pygame.event.get():
    # 閉じるボタン
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    # マウスクリック
    if (event.type == pygame.MOUSEBUTTONDOWN
            and not game.moving and game.shooting_target is None):
      _mouse_event(event.pos, event.button)
    # 右クリックを離したとき、駒説明を非表示にする
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
      game.piece_for_description = None
    # キーボード
    elif (event.type == pygame.KEYDOWN
          and not game.moving and game.shooting_target is None):
      _key_event(event.key, event.mod)
    # スペースキーを離したとき、駒説明を非表示にする
    elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
      game.piece_for_description = None
