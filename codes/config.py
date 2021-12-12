import os

from ctypes import windll
import pygame
import pygame.font
import pygame.image
import pygame.transform

# コマンドライン色
CMD_RED = '\033[31m'
CMD_RESET = '\033[0m'

# ウィンドウサイズ
_DISPLAY_W: int = windll.user32.GetSystemMetrics(0)
_DISPLAY_H: int = windll.user32.GetSystemMetrics(1)
WSIZE = 640 if (_DISPLAY_W < 1920 or _DISPLAY_H < 960) else 960

# ウィンドウアイコン
w_icon = pygame.image.load('../assets/img/B/BUn.png')
w_icon = pygame.transform.scale(w_icon, (32, 32))

pygame.init()

# フォント
cica_path = os.path.normpath(f'{os.path.dirname(__file__)}/../assets/Cica-FChess.ttf')
FONT_JA_16 = pygame.font.Font(cica_path, 16)
FONT_JA_24 = pygame.font.Font(cica_path, 24)
FONT_JA_32 = pygame.font.Font(cica_path, 32)
FONT_EN_16 = pygame.font.SysFont('consolas', 16)
FONT_EN_24 = pygame.font.SysFont('consolas', 24)
FONT_EN_32 = pygame.font.SysFont('consolas', 32)

# 色
AMBER = (209, 140, 71)
BLACK = (0, 0, 0)
BROWN = (153, 102, 51)
CORAL = (255, 127, 127)
LIGHTGREEN = (144, 238, 144)
INK = (51, 51, 51)
IVORY = (255, 206, 158)
ORANGE = (255, 204, 0)
PURPLE = (255, 206, 255)
WISTARIA = (127, 127, 255)
WHITE = (255, 255, 255)
