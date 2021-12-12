'''
dict用
描画などに関する便利な関数を集めたモジュール
'''


import pygame.draw
import pygame.surface
import pygame.transform
from typing import Tuple, Type, Optional
import yaml

from config import FONT_JA_16, FONT_EN_24, FONT_EN_32, WSIZE, BLACK, LIGHTGREEN, IVORY, ORANGE, PURPLE
from dict_config import screen
import draw_utils as du
from pieces.index import *


with open('dict/pieces.yml', encoding='utf8') as file:
  # その頭文字を持つ駒は何か
  # 辞書順に
  yml: 'dict[str, str]' = yaml.safe_load(file)
  pieces: 'dict[str, list[Type[Piece]]]' = {}
  for initial, piece_names in yml.items():
    pieces[initial] = list(map(lambda name: globals()[name], piece_names))


def on_back_button(mousepos: Tuple[int, int]):
  '''
  戻るボタンをクリックしているか

  mousepos : Tuple[int, int]
    マウスの座標
  '''
  return du.on_button(mousepos, (20, 20), (30, 40))


def draw_back_button():
  '''もどるボタンを描画する'''
  surf = pygame.surface.Surface((WSIZE, WSIZE))
  surf.set_colorkey(BLACK)
  surf.set_alpha(180)
  du.draw_triangle(surf, PURPLE, 'L', (20, 40))
  screen.blit(surf, (0, 0))


def _draw_horizontal_lines():
  '''駒の名前を区切る水平線を描画する'''
  pygame.draw.line(screen, IVORY, du.resize(60, 90), du.resize(360, 90), 4)
  for i in range(10):
    pygame.draw.line(screen, IVORY, du.resize(60, 90 + 80 * (i + 1)), du.resize(360, 90 + 80 * (i + 1)))


def _draw_up_button():
  '''上ボタンを描画する'''
  pygame.draw.polygon(screen, ORANGE, (du.resize(180, 50), du.resize(150, 70), du.resize(210, 70)))


def _draw_down_button():
  '''下ボタンを描画する'''
  pygame.draw.polygon(screen, ORANGE, (du.resize(180, 930), du.resize(150, 910), du.resize(210, 910)))


def _draw_list(initial: str, top: int, active_piece: Optional[Type[Piece]]):
  '''
  駒リストを描画する

  initial : str > 'A'-'Z'
    頭文字
  top : int
    上からどれだけスクロールしているか
  active_piece : Optional[Type[Piece]]
    選択中の駒
  '''
  # その頭文字をもつ駒の数
  num = len(pieces[initial])
  # 水平線の描画
  _draw_horizontal_lines()
  # 頭文字の描画
  screen.blit(FONT_EN_32.render(initial, True, IVORY), (90, 30))
  # 駒の名前の描画
  stop = top + 10 if num > top + 10 else num
  for i in range(top, stop):
    font_color = IVORY
    piece_name = pieces[initial][i].__name__
    if active_piece == pieces[initial][i]:
      font_color = LIGHTGREEN
    screen.blit(FONT_EN_24.render(piece_name, True, font_color), (90, 40 + 80 * (i + 1 - top)))
  # 下ボタンの描画
  if num > top + 10:
    _draw_down_button()
  # 上ボタンの描画
  if top > 0:
    _draw_up_button()


def _draw_try_button(img: pygame.surface.Surface):
  '''
  動かしてみるボタン

  img : Surface
    ボタンの ▶ を乗せる駒画像
  '''
  du.draw_triangle(img, ORANGE, 'R', (img.get_width() - 20, img.get_height() - 30))


def _draw_desc_image(active_piece: Type[Piece]):
  '''
  駒の説明の画像を描画する

  active_piece : Optional[Type[Piece]]
    選択中の駒
  '''
  img = du.get_img(f'dict/exp{active_piece.__name__}')
  _draw_try_button(img)
  img = pygame.transform.scale(img, (img.get_width() * WSIZE // 800, img.get_height() * WSIZE // 800))
  screen.blit(img, du.resize(420, 120))


def draw_select_initial_menu():
  '''駒の頭文字を選択するメニューを描画する'''
  # タイトル
  screen.blit(FONT_EN_32.render('Piece Dictionary', True, IVORY), du.resize(40, 40))
  # ボタンと駒数を描画する
  for i in range(26):
    du.draw_button(screen, chr(i + 65),
                   du.resize(20 + (i // 9) * 320, 120 + 90 * (i % 9)), du.resize(140, 60))
    screen.blit(
        FONT_EN_32.render(f'{len(pieces[chr(i + 65)])} items', True, IVORY),
        du.resize(180 + (i // 9) * 320, 120 + 16 + 90 * (i % 9)),
    )
  du.draw_button(screen, '駒の動きの表記',
                 du.resize(20 + 640, 120 + 720), du.resize(140, 60), font=FONT_JA_16)


def draw_notation_manual():
  '''表記法説明'''
  # 画像表示
  img = du.get_img('dict/Notation')
  img = pygame.transform.smoothscale(img, (WSIZE, WSIZE))
  screen.blit(img, (0, 0))
  # もどるボタン
  draw_back_button()


def draw_select_pieces_menu(initial: str, active_piece: Optional[Type[Piece]], top: int):
  '''
  駒を選択するメニューを描画する

  Parameters
  ----------
  initial : str > 'A'-'Z'
    頭文字．
  active_piece : obj
    駒．
  ID_array : dict > {str: int, ...}
    画像IDのディクショナリ．
  top : int
    上からどれだけスクロールしているか
  '''
  # もどるボタン
  draw_back_button()
  # 駒リスト
  _draw_list(initial, top, active_piece)

  if active_piece is not None:
    # 駒の説明の画像の描画
    _draw_desc_image(active_piece)
