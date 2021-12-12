from copy import copy
from typing import Optional, cast

from custom_types import Color, Mode, Position
from games import games, init_960, Placers
from main_config import game, cancel_snd, capture_snd, move_snd, select_snd, play
import pieces.piece_utils as pu
import utils


def decide_game_event(index: int):
  '''ホーム画面でゲームを指定'''
  game.kind = games[index]
  if games[index]['name'] == 'Chess 960':
    game.kind['placers'] = cast(Placers, game.kind['placers'])
    game.kind['placers'][1] = init_960()
  game.select_game = False
  game.select_color = True
  play(select_snd)


def prev_page_event(total: int):
  '''ホーム画面で前のページへ'''
  if game.page > 1:
    game.page -= 1
  else:
    game.page = total
  play(select_snd)


def next_page_event(total: int):
  '''ホーム画面で次のページへ'''
  if game.page < total:
    game.page += 1
  else:
    game.page = 1
  play(select_snd)


def select_color_event(color: Color):
  '''設定画面で色を選択する'''
  game.my_color = color
  play(select_snd)


def select_mode_event(mode: Mode):
  '''設定画面でモードを選択する'''
  game.mode = mode
  game.level = 0 if mode == 'PvsP' else 1
  play(select_snd)


def toggle_foreseeing_event():
  '''設定画面でコンピュータの先読み設定を切り替える'''
  game.foreseeing = False if game.foreseeing else True
  play(select_snd)


def back_event():
  '''設定画面からホーム画面に戻る'''
  game.select_game = True
  game.select_color = False
  play(select_snd)


def start_game_event():
  '''設定画面からゲームを開始する'''
  game.select_color = False
  game.process_after_deciding_kind()
  play(select_snd)
  if game.my_color == 'B' and game.mode == 'PvsC':
    game.computer_moving = True


def back_to_home_event():
  '''ゲーム画面でホーム画面に戻る'''
  game.alert = False
  _page = game.page
  game.__init__()
  game.page = _page
  play(select_snd)


def cancel_back_to_home_event():
  '''ゲーム画面でホーム画面に戻るのをやめる'''
  game.alert = False
  play(cancel_snd)


def archer_attack_event(pos: Optional[Position]):
  '''アーチャーの発射'''
  if pos in game.arrow_targets:
    if game.gameboard[pos].color != game.playersturn:
      del game.gameboard[pos]
      # チェック状態の記録
      game.check_bool = game.is_check(
          'W', game.gameboard) or game.is_check('B', game.gameboard)
      game.stalemate_bool = game.is_stalemate('W') or game.is_stalemate('B')
      game.checkmate_bool = game.cannot_move('W') or game.cannot_move('B')
      play(capture_snd)
    game.shooting_target = pos
    game.time = 0


def move_pieces_event(pos: Optional[Position]):
  '''駒の移動'''
  assert game.kind is not None
  _start = game.startpos
  _board = game.gameboard
  # 駒を移動させる
  # 先にこちらを書かないと駒を取れなくなる
  if _start is not None:
    _piece = _board[_start]
    if _piece.color == game.playersturn and pos in game.valid_moves(_piece, _start):
      game.endpos = pos

      # キャスリングの確認をするか決定
      if game.kind['castling']:
        game.castle_or_not(_piece, game.endpos)
        if game.confirm_castling:
          return

      # アーチャー系駒の攻撃が発生する条件
      # アーチャー系駒であることを示す属性が存在する
      # 移動で取ったときには矢は撃てない
      if hasattr(_piece, 'archer_dir') and game.endpos not in _board:
        # その動きで自分側がチェックされるとき
        _tmp_board = copy(_board)
        _tmp_board[game.endpos] = _piece
        del _tmp_board[_start]
        if game.is_check(game.playersturn, _tmp_board):
          # 取り除かなければならない駒のみに撃てる
          game.arrow_targets = game.arrow_targets_should_removed
          game.arrow_targets_should_removed = set()
        else:
          # その発射で自分側がチェック状態にならない場所のみに撃てる
          game.arrow_targets = (set(utils.arrow_targets_(_piece, _start, game.endpos, _board, pu.rider))
                                - set(game.disallowed_targets))
          game.disallowed_targets = set()
          if game.arrow_targets:
            # 自分の位置にも表示し、矢を打たないというオプションとする
            game.arrow_targets.add(game.endpos)

      game.main()
      game.time = 0
      game.moving = True
      play(move_snd)
      return
  # 動かす駒を選択する
  if pos in _board and not game.prom and not game.confirm_castling:
    game.startpos, game.endpos = pos, None


def promotion_event(index: int):
  '''プロモーション'''
  assert game.kind is not None
  assert game.endpos is not None
  game.gameboard[game.endpos] = game.kind['promote2'][index](game.playersturn)
  game.prom = False
  game.process_after_renewing_board()
  game.endpos = None
  game.time = 0
  game.msg_anim = True


def castling_event():
  '''キャスリング確認後の動き'''
  game.confirm_castling = False
  game.main()
  game.time = 0
  game.moving = True
  play(move_snd)
