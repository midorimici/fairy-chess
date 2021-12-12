import pygame.display
import pygame.time

from config import BROWN
from dict_config import game, screen
import dict_utils as dcu
import draw_utils as du
import utils


def draw():
  '''描画コールバック'''
  screen.fill(BROWN)

  if game.select_initial:
    dcu.draw_select_initial_menu()
  elif game.notation_manual:
    dcu.draw_notation_manual()
  elif game.select_piece:
    dcu.draw_select_pieces_menu(game.initial, game.piece, game.top)
  else:
    _size = game.kind['size']
    _board = game.gameboard
    _start = game.startpos
    _end = game.endpos
    _arw_targets = game.arrow_targets
    _target = game.shooting_target

    du.draw_board(screen, _start, _size, _board,
                  _end if game.moving or _arw_targets == set() else None)

    # 可能な移動先の表示
    if _start is not None and _end is None:
      du.draw_available_moves(
          screen, _size, game.valid_moves(_board[_start], _start, _board))
    # 駒移動アニメーション
    if game.moving:
      assert _start is not None and _end is not None
      du.draw_piece_anim(screen, _size, _board[_end], _start, _end, game.time)
      pygame.time.delay(20)
      game.time += 1
      if game.time >= 10:
        game.moving = False
        game.startpos = None
        if _arw_targets == set():
          game.endpos = None
    # アーチャーの矢の攻撃対象の表示
    if _arw_targets:
      du.draw_arrow_target(screen, _size, game.arrow_targets)
    # 矢射撃アニメーション
    if _target:
      assert _end is not None
      _angle = utils.memo(lambda a, b: 45 * utils.advance_dir(a, b), _end, _target)
      du.draw_arrow_anim(screen, _size, _angle, _end, _target, game.time)
      pygame.time.delay(20)
      game.time += 1
      if game.time >= 10:
        game.shooting_target = None
        game.arrow_targets = set()
        game.endpos = None
    # もどるボタン
    dcu.draw_back_button()

  pygame.display.update()
