'''コンピュータ対戦モード'''


from copy import deepcopy
from random import choice, randint

from custom_types import Color, Board
from pieces.pieces import Pawn
from main import opponent
from utils import value


def cpu_static_value(self, color: Color, count: int, *coef):
  '''
  局面における評価値

  Parameters
  ----------
  self : obj
    基底のオブジェクト．
    属性取り出し用．
  color : Color
    自分の駒色．
  count : int
    開始からの手数．
  *coef : int, ...
    調整の係数．

  Returns
  -------
  : float

  Usus
  ----
  best_move
  max_
  min_

  Utens
  -----
  can_see_square
  gameboard
  valid_moves
  level
  count

  Notes
  -----
  [lv.1]
    自分のトータルスコアと相手のトータルスコアの差(5-35)
    チェックできる(4)
    [終盤]相手のキングのモビリティ(-)(4)
    [終盤]ポーンを突く(4)
    攻撃にさらされている駒がある(-)(5-35)
    [終盤]自分のキングを相手のキングに近づける
  [lv.2]
    相手の駒を攻撃する(2)
    自分の弱い駒を守る
    キャスリング済(6)
    キャスリング前なんだから，キングやルークはあまり動かないでくれよ(-)(4)
  [lv.3]
    自分の攻撃範囲(序盤は中央の支配範囲)
    スキュア/ピンを決めている(2)
    [終盤]チェックメイトしよう・ステイルメイトは避けよう(10)
  [lv.4]
    [序盤]マイナーピースを前に出す
    セブンスルーク(10)
  [lv.5]
    ルーク・クイーンを縦横に重ねる(2)
  '''
  _size: int = self.kind['size']
  _board: Board = self.gameboard
  _level: int = self.level
  _can_see_sq = self.can_see_square
  _valid_moves = self.valid_moves
  _board = self.gameboard

  # 重要度順
  threatened = {}
  rook_on_the_seventh = 0
  checkmate = 0
  stalemate = 0
  checking = 0
  opponent_king_mobility = 0
  pawn_advancing = 0
  castled = 0
  move_before_castling = 0
  skewer = 0
  cross_connection = 0
  threatening = 0
  defended = 0
  king_dist = 0
  attack_range = 0
  minor_front = 0

  # 自分のトータルスコアと相手のトータルスコアの差
  value_dif = value(color, _board) - value(opponent[color], _board)

  # 盤面上のそれぞれの駒の位置，種類について
  for pos, piece in _board.items():
    # 自分の色の駒であるとき
    if piece.color == color:
      # 駒が自分のポーンであるとき
      if piece.abbr == 'P':
        # [終盤]ポーンを突く
        if len(_board) <= _size**2 / 6:
          pawn_advancing += pos[1] if color == 'W' else 7 - pos[1]

  # 攻撃にさらされている駒がある(-)
      # その駒を攻撃している相手の色の駒のリスト
      threatening_pieces = list(_can_see_sq(pos,
                                            [(position, piece) for position, piece in _board.items()
                                             if piece.color == opponent[color]],
                                            _board))
      tmp = deepcopy(_board)
      # その駒を仮に相手色のポーンとして見てみる
      tmp[pos] = Pawn(opponent[color])
      # その駒を攻撃している(守っている)自分の色の駒のリスト
      defending_pieces = list(_can_see_sq(pos,
                                          [(position, piece) for position, piece in tmp.items()
                                           if piece.color == color],
                                          tmp))
      # その駒が相手の色の駒のどれかに攻撃されているとき
      if threatening_pieces:
        threatening_pieces_values = list(map(lambda x: x.value, threatening_pieces))
        threatened[pos] = piece.value
        # 味方の駒に守られている(敵駒だったらそれを攻撃できる味方駒があるか)
        # その駒が自分の色の駒のどれかに攻撃されている(守られている)とき
        if defending_pieces:
          defending_pieces_values = list(map(lambda x: x.value, defending_pieces))
          # 駒の交換が起こり得る最大の回数
          exchange_number = min(len(threatening_pieces_values), len(defending_pieces_values))
          balance = 0
          for number in range(exchange_number):
            # 黒白それぞれが最小価値の駒で交換をしかけたときの損得
            # number + 1 と number でずれるのは，攻防が同量だった場合最後にこちらに1つ駒が残るからその分を除いている
            balance = sum(sorted(threatening_pieces_values)[:(number + 1)]) \
                - sum(sorted(defending_pieces_values)[:number])
            # 交換途中で相手のほうが得をして交換に乗らなくなるとき
            if balance < 0:
              balance = 0
              break
          threatened[pos] = max(0, threatened[pos] - balance)

  # [lv.2]自分の弱い駒を守る
      if _level >= 2:
        # その駒が自分の色の駒のどれかに攻撃されている(守られている)とき
        if defending_pieces:
          # 評価値に加算
          defended += 1

  # [lv.3]自分の攻撃範囲(序盤は中央の支配範囲)
        # その駒を以外すべてを仮に相手色のポーンとして見てみる
        tmp: Board = {position: Pawn(opponent[color])
                      for position in _board}
        tmp[pos] = piece
        if hasattr(piece, 'count'):
          piece_attack_range = piece.available_moves(*pos, tmp,
                                                     size=_size,
                                                     return_capture=True)
        else:
          piece_attack_range = piece.available_moves(*pos, tmp,
                                                     size=_size,
                                                     return_capture=True)
        # 序盤
        if count <= _size * 3 / 2:
          for x, y in piece_attack_range:
            if (_size / 4 <= x < _size * 3 / 4
                    and _size / 4 <= y < _size * 3 / 4):
              attack_range += 1
        else:
          attack_range += len(piece_attack_range)

  # [lv.3]スキュア/ピンを決めている
  # pos, piece -> スキュア/ピンを決めている駒
      if _level >= 3:
        # 攻撃されている駒の位置・名前
        attacked = [position
                    for position in _valid_moves(piece, pos)
                    if position in _board]
        tmp = deepcopy(_board)
        # 攻撃されている(スキュア/ピンを決められて(動けなくなって)いる)駒の位置それぞれについて
        for m_pos in attacked:
          # 攻撃されている駒を取り除いてみる
          del tmp[m_pos]
        # 取り除かれた後の新たな盤面で，攻撃されている駒の名前・オブジェクト
        skewered = {tmp[position].name: tmp[position]
                    for position in _valid_moves(piece, pos, tmp)
                    if position in tmp}
        # 攻撃されている駒の名前リスト
        skwd_pieces = skewered.keys()
        # スキュア/ピンされている背後の駒の価値の総和が評価値
        skewer += sum([skewered[skwd_piece].value for skwd_piece in skwd_pieces])
        # 絶対ピンは高評価
        if 'K' in (skwd_piece[1:] for skwd_piece in skwd_pieces):
          skewer += 10

  # [lv.4][序盤]マイナーピース（ナイト・ビショップ）を前に出す
      if _level >= 4:
        if count <= _size * 3 / 2:
          if piece.abbr in ('N', 'B'):
            if ((piece.color == 'W' and pos[1] > 1)
                    or (piece.color == 'B' and pos[1] < _size - 2)):
              minor_front += 1

  # [lv.5]ルーク・クイーンを縦横に重ねる
      if _level >= 5:
        if piece.abbr in ('R', 'Q'):
          defending_pieces_names = map(lambda x: x.abbr, defending_pieces)
          if 'R' in defending_pieces_names:
            cross_connection += 1
          if 'Q' in defending_pieces_names:
            cross_connection += 1

    # 相手の色の駒であるとき
    if piece.color == opponent[color]:
      # [lv.2]相手の駒を攻撃する
      if _level >= 2:
        if list(_can_see_sq(pos,
                [(position, piece) for position, piece in _board.items()
                    if piece.color == color],
                _board)):
          if piece.abbr != 'K':
            threatening += piece.value

  # [終盤]相手のキングのモビリティ(-)
      if len(_board) <= _size**2 / 6:
        if piece.abbr == 'K':
          opponent_king_mobility = len(_valid_moves(piece, pos))

  threatened_value = sum(threatened.values())

  # [終盤]自分のキングを相手のキングに近づける(距離，-)
  if len(_board) <= _size**2 / 6:
    king_pos = [pos for pos, piece in _board.items() if piece.abbr == 'K']
    king_dist = (king_pos[0][0] - king_pos[1][0])**2 + (king_pos[0][1] - king_pos[1][1])**2

  # [lv.3][終盤]チェックメイトしよう・ステイルメイトは避けよう
    if _level >= 3:
      if self.cannot_move(opponent[color], _board):
        if self.is_stalemate(opponent[color], _board):
          stalemate = 1
        else:
          checkmate = 1

  # チェックできる
  if self.is_check(opponent[color], _board):
    checking = 1

  # [lv.2]キャスリング済
  if _level >= 2:
    if self.finish_castling[color]:
      castled = 1

  # [lv.2]キャスリング前なんだから，キングやルークはあまり動かないでくれよ
    if (not self.finish_castling[color]
            and not all(self.can_castling[color])):
      move_before_castling = 1

  # [lv.4]セブンスルーク(相手の陣地最奥から２番目に自分のルーク)
  if _level >= 4:
    seventh_pos = 1 if color == 'B' else _size - 2
    seventh_pieces = [piece.abbr
                      for pos, piece in _board.items()
                      if pos[1] == seventh_pos]
    if 'R' in seventh_pieces:
      rook_on_the_seventh = 1

  # 終盤補正
  if len(_board) <= _size**2 / 6:
    value_dif *= 2
    threatened_value *= 2
    rook_on_the_seventh /= 10
    cross_connection /= 4
    attack_range = 0

  return (value_dif * coef[0] - threatened_value * coef[1] + rook_on_the_seventh * 10
          + (checkmate - stalemate) * 10 + castled * 6 + checking * 4 - opponent_king_mobility
          + pawn_advancing * 4 - move_before_castling * 4 + skewer * 2 + cross_connection * 2
          + threatening * 2 + defended - king_dist + attack_range + minor_front)


def best_move(self, color: Color, *rand):
  '''
  最適の手(評価値が上位2番目以内の手のうちから選択)を出力

  Parameters
  ----------
  self : obj
    基底のオブジェクト．
    属性取り出し用．
  color : Color
    駒色．
  *rand : int, ...
    調整の係数．

  Returns
  -------
  : tuple > ((int, int), (int, int))
    ((動かす駒の位置), (移動先))

  Usus
  ----
  interact / Draw / computer_move

  Utens
  -----
  valid_moves
  cpu_static_value
  main
  prev_move
  gameboard
  count
  startpos
  endpos
  move_record
  '''
  best_move_dict = {}
  choices_list = {pos: self.valid_moves(piece, pos)
                  for pos, piece in self.gameboard.items()
                  if piece.color == color
                  and self.valid_moves(piece, pos)}

  for startpos, dest in choices_list.items():
    for endpos in dest:
      # print(startpos, endpos)
      self.startpos, self.endpos = startpos, endpos
      self.main()
      best_move_dict[(startpos, endpos)] \
          = cpu_static_value(self, color, self.count, *rand)
      self.prev_move()
      self.move_record.pop(self.count + 1, None)

  if not best_move_dict:
    _ = choice(list(choices_list.items()))
    best_moves = [(_[0], choice(_[1]))]
  else:
    best_moves = [move
                  for move, value in best_move_dict.items()
                  if value >= max(best_move_dict.values()) - 4]
  # print(best_moves, '\n')
  return choice(best_moves)


def max_(self, alpha: int, beta: int, depth: int, color: Color, count: int, *rand):
  '''αβ法により，自分にとって最善の手を，depth 手先まで読んで出力

  Parameters
  ----------
  self : obj
    基底のオブジェクト．
    属性取り出し用．
  alpha, beta : int
  depth : int
    何手先まで読むか．
  color : Color
    駒色．
  count : int
    開始からの手数．cpu_static_value のために必要．
  *rand : int, ...
    調整の係数．

  Returns
  -------
  (maxv, start, end) : tuple > (int, (int, int), (int, int))

  Usus
  ----
  interact / Draw / computer_move

  Utens
  -----
  cpu_static_value
  valid_moves
  main
  min_
  prev_move
  gameboard
  startpos
  endpos
  move_record
  count
  '''
  maxv = -9999
  start = None
  end = None
  evaluation = cpu_static_value(self, color, count, *rand)
  # 読み深さに達する前
  if depth > 0:
    choices_list = {pos: self.valid_moves(piece, pos)
                    for pos, piece in self.gameboard.items()
                    if piece.color == color
                    and self.valid_moves(piece, pos)}
    for startpos, dest in choices_list.items():
      for endpos in dest:
        self.startpos, self.endpos = startpos, endpos
        self.main()
        m = min_(self, alpha, beta, depth - 1, opponent[color], count + 1, *rand)[0]
        if m > maxv:
          maxv = m
          start, end = startpos, endpos
        self.prev_move()
        self.move_record.pop(self.count + 1, None)
        if maxv >= beta:
          return maxv, start, end
        if maxv > alpha:
          alpha = maxv
  # 読み深さに達した
  else:
    maxv = evaluation
  return maxv, start, end


def min_(self, alpha: int, beta: int, depth: int, color: Color, count: int, *rand):
  '''αβ法により，自分にとって最悪の手を，depth 手先まで読んで出力

  Parameters
  ----------
  self : obj
    基底のオブジェクト．
    属性取り出し用．
  alpha, beta : int
  depth : int
    何手先まで読むか．
  color : Color
    駒色．
  count : int
    開始からの手数．cpu_static_value のために必要．
  *rand : int, ...
    調整の係数．

  Returns
  -------
  (minv, start, end) : tuple > (int, (int, int), (int, int))

  Usus
  ----
  interact / Draw / computer_move

  Utens
  -----
  cpu_static_value
  valid_moves
  main
  max_
  prev_move
  gameboard
  startpos
  endpos
  move_record
  count
  '''
  minv = 9999
  start = None
  end = None
  evaluation = cpu_static_value(self, color, count, *rand)
  # 読み深さに達する前
  if depth > 0:
    choices_list = {pos: self.valid_moves(piece, pos)
                    for pos, piece in self.gameboard.items()
                    if piece.color == color
                    and self.valid_moves(piece, pos)}
    for startpos, dest in choices_list.items():
      for endpos in dest:
        self.startpos, self.endpos = startpos, endpos
        self.main()
        m = max_(self, alpha, beta, depth - 1, opponent[color], count + 1, *rand)[0]
        if m < minv:
          minv = m
          start, end = startpos, endpos
        self.prev_move()
        self.move_record.pop(self.count + 1, None)
        if minv <= alpha:
          return minv, start, end
        if minv < beta:
          beta = minv
  # 読み深さに達した
  else:
    minv = evaluation
  return minv, start, end


def computer_move(self):
  '''コンピュータの動き'''
  if self.foreseeing:
    _, self.startpos, self.endpos \
        = max_(self, -9999, 9999, 2, opponent[self.my_color],
               randint(5 * self.level, 35), randint(5 * self.level, 35), randint(2, 6))
  else:
    self.startpos, self.endpos \
        = best_move(self, opponent[self.my_color],
                    randint(5 * self.level, 35), randint(5 * self.level, 35), randint(2, 6))
  self.main()
  self.time = 0
  self.moving = True
  self.computer_moving = False
