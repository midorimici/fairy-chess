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
    if command_args[0] != '_':
      try:
        replace_piece: Type[Piece] = next(piece
                                          for piece in sum(list(dcu.pieces.values()), [])
                                          if piece.abbr == command_args[0])
        game.piece = replace_piece
        game.initial = replace_piece.abbr[0]
      except StopIteration:
        print(f'{CMD_RED}There are no such piece: {command_args[0]}{CMD_RESET}')
        sys.exit(1)
    if len(command_args) >= 2:
      try:
        if command_args[1] != '_':
          replace_piece_around = next(piece
                                      for piece in sum(list(dcu.pieces.values()), [])
                                      if piece.abbr == command_args[1])
          game.kind['placers'] = {
              1: (replace_piece_around,) + (None,) * 10 + (replace_piece_around,),
              3: (None,) * 2 + (replace_piece_around,) + (None,) * 6 + (replace_piece_around,) + (None,) * 2,
          }
      except StopIteration:
        print(f'{CMD_RED}There are no such piece: {command_args[1]}{CMD_RESET}')
        sys.exit(1)
    game.place_pieces()
    game.select_initial = False

  while True:
    draw.draw()
    event.event()


main()
