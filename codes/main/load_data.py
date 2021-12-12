'''ゲームの途中のデータを data.yml にセーブすると、あとからロードできます'''

from typing import TypedDict, List, Tuple, Literal, Optional, cast
import yaml

from custom_types import Piece, Board, Mode
from games import games, GameType
from pieces.index import *

Position = Tuple[int, int]
Color = Literal['W', 'B']
PieceData = TypedDict('PieceData', {
    'position': Position, 'name': str, 'color': Color, 'count': Optional[int]
})
BoardData = List[PieceData]
Data = TypedDict('Data', {
    'pick': bool,
    'game_name_data': str,
    'mode_data': Mode,
    'level_data': int,
    'foreseeing_data': bool,
    'gameboard_data': BoardData,
    'playersturn_data': Color,
    'move_record_data': 'dict[int, Position]',
    'advanced2_pos_data': Position,
    'advanced2_record_data': 'dict[int, Position]',
    'can_castling_data': 'dict[Color, list[bool]]',
    'count_data': int,
    'record_data': 'dict[int, BoardData]',
})

DataToLoad = TypedDict('DataToLoad', {
    'game': GameType,
    'mode': Mode,
    'level': int,
    'foreseeing': bool,
    'gameboard': Board,
    'playersturn': Color,
    'move_record': 'dict[int, Position]',
    'advanced2_pos': Position,
    'advanced2_record': 'dict[int, Position]',
    'can_castling': 'dict[Color, list[bool]]',
    'count': int,
    'record': 'dict[int, Board]',
})


def put_piece(orig_data: PieceData, replace_data: Board):
  pos = orig_data['position']
  name = orig_data['name']
  color = orig_data['color']
  count = orig_data['count']
  piece_to_put: Piece = globals()[name](color)
  if count is not None:
    piece_to_put.count = count
  replace_data[pos] = piece_to_put


try:
  with open('main/data.yml', encoding='utf8') as file:
    yml: 'list[Data]' = yaml.full_load(file)
    for y in yml:
      if y['pick']:
        orig = y
        data = cast(DataToLoad, {key[:-5]: val for key, val in y.items() if key != 'pick'})
        break
    else:
      raise Exception('Specify which data to load by setting its pick to true.')

    data['game'] = next(game for game in games if game['name'] == orig['game_name_data'])

    data['gameboard'] = {}

    for piece in orig['gameboard_data']:
      put_piece(piece, data['gameboard'])

    for number, board in orig['record_data'].items():
      data['record'][number] = {}
      for piece in board:
        put_piece(piece, data['record'][number])
except FileNotFoundError:
  print('Nothing to load.')
