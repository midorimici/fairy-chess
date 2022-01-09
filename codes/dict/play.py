import sys
from typing import Type

from dict_config import game
import dict_utils as dcu
import draw
import event
from pieces.piece import Piece
from config import CMD_RED, CMD_RESET


def main():
  # コマンドラインの第二・第三引数
  # 駒の略記を指定すれば，その駒がテスト盤面にのる
  # 第三引数で指定の駒が周囲に配置される
  command_args = sys.argv[1:]
  if len(command_args) >= 1:
    parse_cmd_args(command_args)
    game.place_pieces()
    game.select_initial = False

  while True:
    draw.draw()
    event.event()


def parse_cmd_args(args: 'list[str]'):
  '''コマンドライン引数を処理する'''
  if args[0] != '_':
    replace_main_piece(args[0])
  if len(args) >= 2:
    replace_surrounding_pieces(args[1])


def replace_main_piece(name: str):
  try:
    replace_piece: Type[Piece] = replacement_piece(name)
    game.piece = replace_piece
    game.initial = replace_piece.abbr[0]
  except StopIteration:
    print(f'{CMD_RED}There are no such piece: {name}{CMD_RESET}')
    sys.exit(1)


def replace_surrounding_pieces(name: str):
  try:
    if name != '_':
      replace_piece_around: Type[Piece] = replacement_piece(name)
      game.kind['placers'] = {
          1: (replace_piece_around,) + (None,) * 10 + (replace_piece_around,),
          3: (None,) * 2 + (replace_piece_around,) + (None,) * 6 + (replace_piece_around,) + (None,) * 2,
      }
  except StopIteration:
    print(f'{CMD_RED}There are no such piece: {name}{CMD_RESET}')
    sys.exit(1)


def replacement_piece(name: str) -> Type[Piece]:
  '''駒の名前から駒クラスを取得'''
  return next(piece
              for piece in sum(list(dcu.pieces.values()), [])
              if piece.abbr == name)


main()
