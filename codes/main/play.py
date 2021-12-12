'''
ゲームとして全体を動かすときはこれを指定する
'''

import sys
from traceback import print_exc

from main_config import game
import draw
import event
import utils


def main():
  args = sys.argv

  # コマンドラインで色引数が指定されたとき
  if 'W' in args or 'B' in args:
    game.load_data()
    game.my_color = 'W' if 'W' in args else 'B'
    game.select_game = False
    game.refresh_memo()

  while True:
    draw.draw()
    event.event()


try:
  main()
except Exception:
  print('Oh, it seems that you caught an error....\n')
  print('*' * 12)
  print_exc()
  print('*' * 12)
  print('\nSave the data in data.yml...\n')
  utils.save_print(game, error=True)
  sys.exit(1)
