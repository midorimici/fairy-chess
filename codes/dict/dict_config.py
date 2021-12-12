import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pygame.display

from config import WSIZE, w_icon
from dictionary import Game

# ウィンドウの位置
os.environ['SDL_VIDEO_WINDOW_POS'] = '0,32'

pygame.display.set_icon(w_icon)
screen = pygame.display.set_mode((WSIZE, WSIZE))
pygame.display.set_caption('Piece Dictionary')

game = Game()
