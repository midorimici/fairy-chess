import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pygame.display
import pygame.mixer

from config import WSIZE, w_icon
from main import Game

# 音声の設定
pygame.mixer.init()
_snd = pygame.mixer.Sound
_snd_dir = '../assets/sounds/'
select_snd = _snd(f'{_snd_dir}select.wav')
cancel_snd = _snd(f'{_snd_dir}cancel.wav')
move_snd = _snd(f'{_snd_dir}move.wav')
capture_snd = _snd(f'{_snd_dir}capture.wav')
check_snd = _snd(f'{_snd_dir}check.wav')

_muted = False
# コマンドラインで m が指定されたとき
if 'm' in sys.argv:
  # ミュートにする
  _muted = True

# ウィンドウの位置
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,32'

pygame.display.set_icon(w_icon)
screen = pygame.display.set_mode((WSIZE, WSIZE))
pygame.display.set_caption('Fairy Chess')

game = Game()

opponent = {'W': 'B', 'B': 'W'}


def play(sound: pygame.mixer.Sound):
  if not _muted:
    sound.play()
