import pygame.display
import pygame.draw
import pygame.rect
import pygame.surface
import pygame.time
import pygame.transform

import computer
from config import (FONT_EN_16, FONT_EN_24, FONT_EN_32, FONT_JA_24, FONT_JA_32,
                    BLACK, BROWN, CORAL, IVORY, LIGHTGREEN, ORANGE, PURPLE, WHITE, WISTARIA)
import draw_utils as du
from games import games
from main_config import game, screen, check_snd, move_snd, play
import utils


def _draw_game_menu():
  '''ゲーム選択メニューを描画する'''
  _page = game.page
  base_index = 10 * (_page - 1)
  # ゲームボタン
  for i in range(2):
    for j in range(5):
      index = base_index + 5 * i + j
      if index < len(games):
        du.draw_button(
            screen, games[index]['name'],
            du.resize(40 + 460 * i, 40 + 160 * j), du.resize(420, 120),
            font=FONT_EN_24,
        )
        screen.blit(
            FONT_EN_16.render(str(index % 10), True, WHITE),
            du.resize(20 + 460 * i, 40 + 160 * j),
        )
  # ページ切り替えボタン
  du.draw_triangle(screen, LIGHTGREEN, 'L', (360, 880))
  du.draw_triangle(screen, LIGHTGREEN, 'R', (600, 880))
  screen.blit(FONT_EN_32.render('PREV', True, LIGHTGREEN), du.resize(260, 866))
  screen.blit(FONT_EN_32.render('NEXT', True, LIGHTGREEN), du.resize(630, 866))
  # 現在のページ数
  page_text = f'{_page}/{len(games) // 10 + 1}'
  screen.blit(
      FONT_EN_32.render(page_text, True, WHITE),
      du.resize(480 - FONT_EN_32.size(page_text)[0] // 2, 866),
  )


def _draw_setting_menu():
  '''設定画面を描画する'''
  assert game.kind is not None
  _color = game.my_color
  _mode = game.mode
  _level = game.level
  _foreseeing = game.foreseeing
  # ゲーム名を表示する
  _rendered_game_name = FONT_EN_24.render(game.kind['name'], True, IVORY)
  screen.blit(
      _rendered_game_name,
      du.resize(480 - _rendered_game_name.get_width() // 2, 60),
  )
  # 色選択
  screen.blit(
      FONT_JA_32.render('あなたの駒の色を選んでね', True, IVORY),
      du.resize(120, 180),
  )
  if _color == 'W':
    du.draw_button(screen, '✓White  ',
                   du.resize(120, 270), du.resize(300, 120), color=BLACK, bgcolor=WHITE, font=FONT_JA_32)
    du.draw_button(screen, '  Black  ',
                   du.resize(540, 270), du.resize(300, 120), color=WHITE, bgcolor=BLACK, font=FONT_JA_32)
  elif _color == 'B':
    du.draw_button(screen, '  White  ',
                   du.resize(120, 270), du.resize(300, 120), color=BLACK, bgcolor=WHITE, font=FONT_JA_32)
    du.draw_button(screen, '✓Black  ',
                   du.resize(540, 270), du.resize(300, 120), color=WHITE, bgcolor=BLACK, font=FONT_JA_32)

  # モード選択
  screen.blit(
      FONT_JA_32.render('人と対戦かコンピュータ対戦か選んでね', True, IVORY),
      du.resize(120, 480),
  )
  if _mode == 'PvsP':
    du.draw_button(screen, '✓人と対戦 ',
                   du.resize(120, 570), du.resize(300, 120), bgcolor=PURPLE, font=FONT_JA_24)
    du.draw_button(screen, '  コンピュータと対戦 ',
                   du.resize(540, 570), du.resize(300, 120), font=FONT_JA_24)
  elif _mode == 'PvsC':
    du.draw_button(screen, '  人と対戦 ',
                   du.resize(120, 570), du.resize(300, 120), font=FONT_JA_24)
    du.draw_button(screen, '✓コンピュータと対戦 ',
                   du.resize(540, 570), du.resize(300, 120), bgcolor=PURPLE, font=FONT_JA_24)

  if _level:
    # レベル選択
    screen.blit(
        FONT_JA_32.render('レベル', True, IVORY),
        du.resize(120, 750),
    )
    for i in range(1, 6):
      if _level == i:
        _text = f'✓{i}'
      else:
        _text = f'  {i}'
      screen.blit(
          FONT_JA_32.render(_text, True, IVORY),
          du.resize(180 + 120 * i, 750),
      )

    # 先読みの有無
    screen.blit(
        FONT_JA_32.render('先読み', True, IVORY),
        du.resize(120, 840),
    )
    du.draw_button(screen, '✓' if _foreseeing else '  ',
                   du.resize(300, 840), du.resize(40, 40), color=BROWN, font=FONT_JA_32)

  # もどる
  du.draw_button(screen, '←もどる', du.resize(30, 30), du.resize(210, 90), font=FONT_JA_32)

  # 決定
  du.draw_button(screen, 'PLAY!', du.resize(720, 30), du.resize(210, 90), color=BROWN, bgcolor=ORANGE)


def _draw_balloon(width: int, height: int, point: 'tuple[int, int]'):
  '''
  吹き出しを描画する

  width : int
    幅
  height : int
    高さ
  point : Tuple[int, int]
    吹き出しの先の盤面座標
  '''
  assert game.kind is not None
  _rect_left = 480 - width // 2
  _rect_top = 480 - height // 2
  rect = pygame.rect.Rect(
      du.resize(_rect_left, _rect_top),
      du.resize(width, height),
  )
  pygame.draw.rect(screen, PURPLE, rect, border_radius=16)
  pygame.draw.polygon(screen, PURPLE, (
      du.resize(480 - width // 4, 480),
      du.resize(480 + width // 4, 480),
      du.to_win_coord(point, game.kind['size']),
  ))


def _draw_promotion_balloon():
  '''プロモーションのときの吹き出しを描画する'''
  assert game.endpos is not None
  assert game.kind is not None
  _end = game.endpos
  if game.my_color == 'B':
    _end = (game.kind['size'] - 1 - _end[0], game.kind['size'] - 1 - _end[1])
  _num = len(game.kind['promote2'])
  _piece_size = int(du.square_size(game.kind['size']))
  _area_size = _piece_size + 30
  # 吹き出し
  _rect_width = _area_size * (_num % 4 if _num < 4 else 4)
  _rect_height = _area_size * (1 + (_num - 1) // 4)
  _draw_balloon(_rect_width, _rect_height, _end)

  def _left_top(i):
    return du.resize(
        (480 - _rect_width // 2) + 15 + _area_size * (i % 4),
        (480 - _rect_height // 2) + 15 + _area_size * (i // 4),
    )
  # [キーボード] 選択中の駒
  _index = game.selecting_prom_piece_index
  if _index is not None:
    pygame.draw.rect(
        screen, WISTARIA, pygame.rect.Rect(_left_top(_index), (_piece_size, _piece_size))
    )
  # 駒
  for i in range(_num):
    _piece = game.kind['promote2'][i](game.playersturn)
    du.draw_piece(screen, _piece, _left_top(i), _piece_size)


def _draw_castling_confirmation():
  '''キャスリング確認のときの吹き出しを描画する'''
  assert game.endpos is not None
  assert game.kind is not None
  _end = game.endpos
  if game.my_color == 'B':
    _end = (game.kind['size'] - 1 - _end[0], game.kind['size'] - 1 - _end[1])
  # 吹き出し
  _draw_balloon(480, 240, _end)
  # テキスト
  rendered_text = FONT_JA_32.render('キャスリング？', True, WISTARIA)
  screen.blit(
      rendered_text,
      du.resize(480 - rendered_text.get_width() // 2, 420),
  )
  # ボタン
  du.draw_button(screen, 'Yes', du.resize(360, 480), du.resize(90, 60), color=WISTARIA, bgcolor=PURPLE)
  du.draw_button(screen, 'No', du.resize(510, 480), du.resize(90, 60), color=WISTARIA, bgcolor=PURPLE)


def _draw_piece_value():
  '''駒の価値を表示する'''
  w_val, b_val = utils.memo(
      lambda b: (utils.value('W', b), utils.value('B', b)), game.gameboard
  )
  # モーダル
  rect = pygame.rect.Rect(du.resize(180, 390), du.resize(600, 180))
  pygame.draw.rect(screen, PURPLE, rect, border_radius=16)
  # テキスト
  white_text_surf = FONT_EN_32.render('WHITE', True, WISTARIA)
  text_width = white_text_surf.get_width()
  screen.blit(
      white_text_surf,
      du.resize(480 - 2 * text_width, 430),
  )
  screen.blit(
      FONT_EN_32.render('BLACK', True, WISTARIA),
      du.resize(480 + text_width, 430),
  )
  # 価値
  w_val_text_surf = FONT_EN_32.render(str(w_val), True, WISTARIA)
  screen.blit(
      w_val_text_surf,
      (480 - 2 * text_width + (text_width - w_val_text_surf.get_width()), 500),
  )
  b_val_text_surf = FONT_EN_32.render(str(b_val), True, WISTARIA)
  screen.blit(
      b_val_text_surf,
      (480 + text_width + (text_width - b_val_text_surf.get_width()), 500),
  )


def _draw_user_guide():
  '''操作方法説明の描画'''
  # モーダル
  rect = pygame.rect.Rect(du.resize(60, 120), du.resize(840, 720))
  pygame.draw.rect(screen, PURPLE, rect, border_radius=16)

  # テキスト
  def render_text(text: str):
    return FONT_JA_24.render(text, True, WISTARIA)
  screen.blit(render_text('[z]/[x]                      前/次の盤面'), du.resize(90, 160))
  screen.blit(render_text('[v]                          駒の価値の表示/非表示'), du.resize(90, 220))
  screen.blit(render_text('[?]                          ヘルプの表示/非表示'), du.resize(90, 280))
  screen.blit(render_text('[backspace]                  ホーム画面に戻る'), du.resize(90, 340))
  screen.blit(render_text('[ctrl][s]                    ゲームデータをセーブする'), du.resize(90, 400))
  screen.blit(render_text('[ctrl][l]                    ゲームデータをロードする'), du.resize(90, 460))
  screen.blit(render_text('[h][j][k][l]                 左/下/上/右のマスを選択'), du.resize(90, 520))
  screen.blit(render_text('[H][J][K][L]                 左/下/上/右の次の駒があるマスを選択'), du.resize(90, 580))
  screen.blit(render_text('[e][r][d][f]                 左上/右上/左下/右下のマスを選択'), du.resize(90, 640))
  screen.blit(render_text('[n][N]                       次/前の候補マスを選択'), du.resize(90, 700))
  screen.blit(render_text('[g] - <file, rank> - [enter] 指定のファイル・ランクのマスを選択'), du.resize(90, 760))


def _draw_alert():
  '''ゲーム選択画面に戻るときの確認ウィンドウの描画'''
  # モーダル
  rect = pygame.rect.Rect(du.resize(60, 390), du.resize(840, 180))
  pygame.draw.rect(screen, PURPLE, rect, border_radius=16)
  # テキスト
  rendered_text = FONT_JA_32.render('ゲームを中断してホーム画面に戻りますか？', True, WISTARIA)
  screen.blit(
      rendered_text,
      du.resize(480 - rendered_text.get_width() // 2, 420),
  )
  # ボタン
  du.draw_button(screen, 'Yes', du.resize(360, 480), du.resize(90, 60), color=WISTARIA, bgcolor=PURPLE)
  du.draw_button(screen, 'No', du.resize(510, 480), du.resize(90, 60), color=WISTARIA, bgcolor=PURPLE)


def _draw_piece_move_anim():
  '''駒移動アニメーション'''
  assert game.kind is not None
  assert game.startpos is not None
  assert game.endpos is not None
  du.draw_piece_anim(
      screen, game.kind['size'],
      game.gameboard[game.endpos], game.startpos, game.endpos,
      game.time, game.my_color == 'B',
  )
  pygame.time.delay(20)
  game.time += 1
  if game.time >= 10:
    game.moving = False
    game.startpos = None
    if game.arrow_targets == set() and not game.prom:
      game.endpos = None
      game.time = 0
      game.msg_anim = True
      if game.mode == 'PvsC':
        game.computer_moving = True


def _shooting_anim():
  '''矢射撃アニメーション'''
  assert game.kind is not None
  assert game.endpos is not None
  assert game.shooting_target is not None
  _angle = utils.memo(lambda a, b: 45 * utils.advance_dir(a, b), game.endpos, game.shooting_target)
  du.draw_arrow_anim(
      screen, game.kind['size'], _angle, game.endpos,
      game.shooting_target, game.time, game.my_color == 'B',
  )
  pygame.time.delay(20)
  game.time += 1
  if game.time >= 10:
    game.shooting_target = None
    game.arrow_targets = set()
    game.process_after_renewing_board()
    game.endpos = None
    game.time = 0
    game.msg_anim = True
    if game.mode == 'PvsC':
      game.computer_moving = True


def _message_anim():
  '''チェック・チェックメイトなどのメッセージの表示アニメーション'''
  _draw_message()
  pygame.time.delay(20)
  game.time += 1
  if game.time == 1:
    play(check_snd)
  elif game.time >= 30:
    game.msg_anim = False


def _draw_message():
  '''メッセージを描画する'''
  # 不透明度
  opacity = 240 - 8 * game.time

  bgcolor = WHITE
  text_color = WHITE
  text = ''

  if game.stalemate_bool:
    bgcolor = LIGHTGREEN
    text_color = WHITE
    text = 'Stalemate.'
  elif game.checkmate_bool:
    bgcolor = CORAL
    text_color = WHITE
    text = 'Checkmate!'
  elif game.check_bool:
    bgcolor = ORANGE
    text_color = WHITE
    text = 'Check!'

  surf = pygame.surface.Surface(du.resize(960, 120))
  surf.set_alpha(opacity)
  surf.fill(bgcolor)
  surf.blit(
      FONT_EN_32.render(text, True, text_color),
      du.resize((960 - FONT_EN_32.size(text)[0]) // 2, (120 - FONT_EN_32.size(text)[1]) // 2),
  )
  screen.blit(surf, du.resize(0, 420))


def _draw_piece_description():
  '''駒の説明画像を表示する'''
  img = du.get_img(f'dict/exp{game.piece_for_description}')
  img.set_alpha(85 * game.time)
  img_size = (img.get_width() * 1080 // img.get_height(), 1080)
  img = pygame.transform.scale(
      img, list(map(int, du.resize(*img_size))))
  screen.blit(img, du.resize(960 - img_size[0], 0))


def _draw_animations():
  '''アニメーションの描画を処理する'''
  assert game.kind is not None
  _size = game.kind['size']
  _start = game.startpos
  _target = game.shooting_target
  # 駒移動アニメーション
  if game.moving and not game.confirm_castling:
    _draw_piece_move_anim()
  # 矢射撃アニメーション
  elif _target is not None:
    _shooting_anim()
  # チェック・チェックメイトなどのメッセージの表示アニメーション
  elif game.msg_anim and (game.check_bool or game.checkmate_bool):
    _message_anim()
  # 駒の説明を表示する
  elif game.piece_for_description is not None:
    _draw_piece_description()
    pygame.time.delay(20)
    if game.time < 3:
      game.time += 1
  # コンピュータ
  elif (game.computer_moving
        and game.playersturn != game.my_color
        and not game.checkmate_bool):
    du.draw_board(screen, _start, _size, game.gameboard, is_black=game.my_color == 'B')
    pygame.display.update()
    computer.computer_move(game)
    play(move_snd)


def draw():
  '''描画コールバック'''
  screen.fill(BROWN)

  if game.select_game:
    _draw_game_menu()
  elif game.select_color:
    _draw_setting_menu()
  else:
    assert game.kind is not None
    _size = game.kind['size']
    _board = game.gameboard
    _start = game.startpos
    _end = game.endpos
    _arw_targets = game.arrow_targets

    du.draw_board(screen, _start, _size, _board,
                  hide=_end if game.moving or _arw_targets == set() else None,
                  selected=game.selecting_square,
                  is_black=game.my_color == 'B')

    # 可能な移動先の表示
    if _start is not None and _end is None:
      _piece = _board[_start]
      du.draw_available_moves(
          screen, _size, set(game.valid_moves(_piece, _start)),
          change_color_condition=game.playersturn != _piece.color,
          is_black=game.my_color == 'B',
      )
    # アーチャーの矢の攻撃対象の表示
    if _arw_targets:
      du.draw_arrow_target(screen, _size, game.arrow_targets, game.my_color == 'B')

    # プロモーション
    if game.prom:
      _draw_promotion_balloon()
    # キャスリングするかどうかの確認
    if game.confirm_castling:
      _draw_castling_confirmation()

    # 駒の価値の表示
    if game.show_value:
      _draw_piece_value()
    # ヘルプの表示
    if game.show_user_guide:
      _draw_user_guide()
    # ゲーム選択メニューに戻るかの確認
    if game.alert:
      _draw_alert()

    _draw_animations()

    du.draw_cmd(screen, game.cmd_repeat_num, game.dest_cmd)

  pygame.display.update()
