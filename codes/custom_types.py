from typing import Dict, Optional, Tuple, Literal, Type

from pieces.piece import Piece, PositionList, PositionSet

Color = Literal['W', 'B']
Mode = Literal['PvsP', 'PvsC']
Position = Tuple[int, int]
Board = Dict[Position, Piece]
Placers = Dict[int, Tuple[Optional[Type[Piece]], ...]]
AsymPlacers = Dict[int, Tuple[Optional[Tuple[Type[Piece], Color]], ...]]
