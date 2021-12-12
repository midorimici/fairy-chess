'''ゲームのルールを決めたり進行を管理したりするモジュール

相手の駒色の辞書の定義
Game クラスの定義

Notes
-----
chess python と検索をかけたら，以下のサイトが出てきたので，これを修正・拡張しています．
https://gist.github.com/rsheldiii/2993225
もとのコメント(英語)は消してありますが，原文はこちらのサイトでも見れます．
'''


from copy import copy, deepcopy
from typing import Tuple, Optional, Literal, cast

from custom_types import Position, PositionSet, Board, Color, Mode
from games import GameType, Placers, AsymPlacers
from pieces import pieces
from pieces.fairy_pieces3 import Orphan, Friend
import pieces.piece_utils as pu
import utils


# 相手の駒色
opponent: 'dict[Color, Color]' = {'W': 'B', 'B': 'W'}


class Game:
  '''ゲームのルールを決めたり進行を管理したりするクラス'''

  def __init__(self):
    # モード : str
    self.mode: Mode = 'PvsP'
    # コンピュータの強さ : int > 1-5
    self.level: int = 0
    # コンピュータ先読み有無 : bool
    self.foreseeing: bool = False
    # ゲームの種類 : GameType
    self.kind: Optional[GameType] = None
    # ターン : str > 'W', 'B'
    self.playersturn: Color = 'W'
    # 盤面 : dict
    # {(int, int): Piece, ...}
    self.gameboard: Board = {}
    # ルークの初期位置
    self.rook_init_pos: Optional[Tuple[int, int]] = None
    self.king_init_pos: Optional[int] = None
    # アンパッサン
    # 直前にポーンが2歩前進したか : Position | None
    self.advanced2_pos: Optional[Position] = None
    # advanced2 の記録 : dict > {int: Position, ...}
    self.advanced2_record: 'dict[int, Position]' = {}
    # アンパッサンできるか : bool
    self.en_passant: bool = False
    # 回数によって動きが変わる駒の移動の記録
    self.move_record: 'dict[int, Position]' = {}
    # キャスリング
    # キャスリングのポテンシャルが残っているか : dict > {'W': [bool, bool], 'B': ...}
    self.can_castling: 'dict[Color, list[bool]]' = {'W': [True, True], 'B': [True, True]}
    self.can_castling_tmp = copy(self.can_castling)
    # キャスリングするかどうかをプレイヤーに確認するか : bool
    self.confirm_castling: bool = False
    # キャスリングするかの確認の後，キャスリングすることをプレイヤーが選択したか : bool
    self.do_castling: bool = False
    # 何手目で何色のどちら側のキャスリングの可能性がなくなったかの記録:
    # dict > {int: ((Color, 0), (Color, 1)), ...}
    self.give_up_castling: 'dict[int, tuple[tuple[Color, Literal[0]], tuple[Color, Literal[1]]]]' = {}
    # キャスリングが何手目で完了したか : dict > {'W': int, 'B': int}
    self.finish_castling: 'dict[Color, int]' = {'W': 0, 'B': 0}
    self.finish_castling_tmp: 'dict[Color, int]' = {}
    # プロモーション : bool
    self.prom: bool = False
    # ゲーム選択 : bool
    self.select_game: bool = True
    # 表示ページ : int > 1-
    self.page: int = 1
    # 駒色選択 : bool
    self.select_color: bool = False
    # 自分の色 : str > 'W', 'B'
    self.my_color: Color = 'W'
    # 説明を表示する駒の名前 : str | None
    self.piece_for_description: Optional[str] = None
    # 駒の価値を表示する : bool
    self.show_value: bool = False
    # ヘルプを表示する : bool
    self.show_user_guide: bool = False
    # ゲーム選択メニューに戻るかの確認 : bool
    self.alert: bool = False
    # 状態
    self.check_bool: bool = False
    self.stalemate_bool: bool = False
    self.checkmate_bool: bool = False
    # 記録
    self.record: 'dict[int, Board]' = {}
    self.count: int = 0

    # アニメーション
    # 駒がアニメーション中 : bool
    self.moving: bool = False
    # メッセージアニメーション中 : bool
    self.msg_anim: bool = False
    # 矢を撃つ場所 : tuple > (int, int)
    self.shooting_target: Optional[Position] = None
    # コンピュータが動作中 : bool
    self.computer_moving = False
    # アニメーションのコマ数 : int
    self.time: int = 1
    # 始点・終点 : tuple > (int, int)
    self.startpos: Optional[Position] = None
    self.endpos: Optional[Position] = None

    # アーチャーの矢の可能な攻撃対象 : PositionSet
    self.arrow_targets: PositionSet = set()
    # チェックを阻止するために取り除く必要がある駒の位置 set
    self.arrow_targets_should_removed: PositionSet = set()
    # アーチャーの矢でチェックのため攻撃できない対象 : PositionSet
    self.disallowed_targets: PositionSet = set()

    # [キーボード] 選択中のプロモーション先
    self.selecting_prom_piece_index: Optional[int] = None
    # [キーボード] 選択中のマス
    self.selecting_square: Optional[Position] = None
    # [キーボード] コマンド繰り返し指定の数値
    self.cmd_repeat_num: Optional[str] = None
    # [キーボード] 移動先として指定されたマスを表すコマンド
    self.dest_cmd: Optional[str] = None

  def process_after_deciding_kind(self):
    '''ゲーム種類決定後の処理'''
    # ルーク・キングの初期位置の記録
    assert self.kind is not None
    if self.kind['castling']:
      self.rook_init_pos = utils.rook_init_pos(cast(Placers, self.kind['placers']))
      self.king_init_pos = utils.king_init_pos(cast(Placers, self.kind['placers']))
    # 駒の配置
    self.place_pieces()
    self.refresh_memo()
    self.move_record = {}
    # データの保持
    self.record = {0: deepcopy(self.gameboard)}
    self.count = 0

  def place_pieces(self):
    '''駒を盤面に配置する'''
    assert self.kind is not None
    if self.kind['asym']:
      placers = cast(AsymPlacers, self.kind['placers'])
      for fl in range(self.kind['size']):
        for rk in placers:
          # None を指定すれば駒が置かれることはなく次のマスへ進む
          _ = placers[rk][fl]
          if _ is not None:
            self.gameboard[(fl, rk - 1)] = _[0](_[1])
    else:
      placers = cast(Placers, self.kind['placers'])
      for fl in range(self.kind['size']):
        for rk in placers:
          piece = placers[rk][fl]
          # None を指定すれば駒が置かれることはなく次のマスへ進む
          if piece is not None:
            # 白の駒
            self.gameboard[(fl, rk - 1)] = piece('W')
            # 黒の駒
            self.gameboard[(fl, self.kind['size'] - rk)] = piece('B')

  def main(self):
    '''盤面の状態の変更'''
    startpos, endpos = self.startpos, self.endpos
    # 開始位置・終了位置がともに指定されている
    if startpos is not None and endpos is not None:
      # 動かす駒を取得
      target = self.gameboard.get(startpos)

      # 開始位置に駒が存在し，その色が自分の駒色である
      if target and target.color == self.playersturn:
        assert self.kind is not None
        # 駒を動かした回数によって動きが変わる駒が動いた
        if hasattr(target, 'count'):
          target.count += 1
        # ポーンが2歩進んだ
        if (target.abbr == 'P'
                and endpos[1] == startpos[1] + (2 if target.color == 'W' else -2)):
          self.advanced2_pos = endpos
        else:
          self.advanced2_pos = None
        # --キャスリング
        if self.kind['castling']:
          self.can_castling_tmp = deepcopy(self.can_castling)
          # -キングが動いた
          if target.name == 'WK':
            self.can_castling['W'] = [False, False]
          if target.name == 'BK':
            self.can_castling['B'] = [False, False]
          # -ルークが動いた
          assert self.rook_init_pos is not None
          if target.name == 'WR':
            if startpos[0] == self.rook_init_pos[0]:
              self.can_castling['W'][0] = False
            if startpos[0] == self.rook_init_pos[1]:
              self.can_castling['W'][1] = False
          if target.name == 'BR':
            if startpos[0] == self.rook_init_pos[0]:
              self.can_castling['B'][0] = False
            if startpos[0] == self.rook_init_pos[1]:
              self.can_castling['B'][1] = False
        # 通常の動き
        self.renew_gameboard(
            startpos, endpos, self.gameboard, target.color)
        self.promotion(target, endpos)
        self.process_after_renewing_board()

  def valid_moves(
      self, piece: pieces.Piece, startpos: Position, gameboard: 'Optional[Board]' = None,
  ):
    '''
    動ける位置を出力．味方駒上には移動不可．

    Parameters
    ----------
    piece : Piece
      駒．
    startpos : tuple > (int, int)
      開始位置．絶対座標．
    gameboard : dict > {(int, int): obj, ...} | None
      与えられたとき、シミュレーションで使う盤面
      実際の盤面を使うときは None

    Returns
    -------
    : list > [(int, int), ...]
    '''
    assert self.kind is not None

    if piece.moves is not None and gameboard is None and not piece.recalc:
      return piece.moves

    _board = gameboard or self.gameboard
    _size = self.kind['size']

    if utils.in_zone(_board, 1, startpos, 'Bz') and piece.abbr not in ('Mi', 'Bz'):
      # ブリザード範囲内
      result: PositionSet = set()
    elif utils.in_zone(_board, 2, startpos, 'Mi') and piece.abbr not in ('Mi', 'Bz'):
      # ミスト範囲内
      result = (pieces.King('W').available_moves(*startpos, _board, size=_size)
                if piece.color == 'W'
                else pieces.King('B').available_moves(*startpos, _board, size=_size))
    else:
      result = piece.available_moves(*startpos, _board, size=_size)
      # アンパッサン
      self.en_passant = False
      if piece.abbr == 'P':
        for endpos in ((x, y - (1 if piece.color == 'W' else -1))
                       for x, y in utils.pawn_init_pos(
                self.kind['placers'], _size,
                self.kind['asym'])[opponent[piece.color]]):
          if self.en_passant_requirements(piece, startpos, endpos):
            self.en_passant = True
            result.add(endpos)
      # キャスリング
      if self.kind['castling']:
        for endpos in [(2, 0), (_size - 2, 0), (2, _size - 1),
                       (_size - 2, _size - 1)]:
          if self.castling_requirements(piece, endpos, 0, self.gameboard, self.can_castling):
            result.add(endpos)
          if self.castling_requirements(piece, endpos, 1, self.gameboard, self.can_castling):
            result.add(endpos)
    # 盤面の中に収まらなければならない
    result = {pos for pos in result
              if pu.is_in_bounds(*pos, _size)}
    # チェック回避のため動き縛り
    result_tmp = copy(result)
    if hasattr(piece, 'archer_dir'):
      # 動かす駒がアーチャーのとき
      for endpos in result_tmp:
        gameboard_tmp = copy(_board)
        self.renew_gameboard(
            startpos, endpos, gameboard_tmp, piece.color)
        # 動いた
        if not self.is_check(piece.color, gameboard_tmp):
          # 動いてもチェックにならないとき動けるが
          # 相手の何かの駒を矢で取るとこちらがチェックされるとき
          # その位置に矢を射ることはできない
          for target in utils.arrow_targets_(
                  piece, startpos, endpos, gameboard_tmp, pu.rider):
            # 矢で撃てる駒をそれぞれ取り除いてみる
            target_tmp = gameboard_tmp[target]
            del gameboard_tmp[target]
            if self.is_check(piece.color, gameboard_tmp):
              # 取り除いた結果自分がチェックされるならそこには撃てない
              self.disallowed_targets.add(target)
            gameboard_tmp[target] = target_tmp
        # 矢で取った
        else:
          # 動いたらチェックになるとき、チェックしている駒を矢で取るしかない
          for target in utils.arrow_targets_(
                  piece, startpos, endpos, gameboard_tmp, pu.rider):
            # 矢で撃てる駒をそれぞれ取り除いてみる
            target_tmp = gameboard_tmp[target]
            del gameboard_tmp[target]
            if self.is_check(piece.color, gameboard_tmp):
              # 取り除いてもチェック解除されないなら戻す
              gameboard_tmp[target] = target_tmp
            else:
              # 取り除いたらチェック解除できるなら、その駒を登録する
              self.arrow_targets_should_removed += target
          else:
            # 矢で取り除いてもチェック解除されないなら、
            # その動きでチェックを解除することはできない
            result.remove(endpos)
    else:
      for endpos in result_tmp:
        gameboard_tmp = deepcopy(_board)
        self.renew_gameboard(
            startpos, endpos, gameboard_tmp, piece.color)
        self.refresh_memo(gameboard_tmp)
        if self.is_check(piece.color, gameboard_tmp):
          result.remove(endpos)

    piece.moves = sorted(result)
    piece.recalc = False
    return piece.moves

  def en_passant_requirements(self, piece: pieces.Piece, startpos: Position, endpos: Position):
    '''
    アンパッサンの条件を満たす

    Parameters
    ----------
    piece : Piece
      駒．
    startpos, endpos : tuple > (int, int)
      開始位置，終了位置．絶対座標．

    Returns
    -------
    : bool

    Notes
    -----
    https://midorimici.com/posts/chess-app-devel-10/#%E3%82%A2%E3%83%B3%E3%83%91%E3%83%83%E3%82%B5%E3%83%B3%E3%81%AE%E6%9D%A1%E4%BB%B6%E5%BC%8F%E3%82%92%E5%AE%9A%E7%BE%A9%E3%81%99%E3%82%8B
    '''
    _direction = 1 if piece.color == 'W' else -1
    return (piece.abbr == 'P'
            and self.advanced2_pos
            and startpos[1] == endpos[1] - _direction
            and startpos[1] == self.advanced2_pos[1]
            and endpos[1] == self.advanced2_pos[1] + _direction
            and abs(startpos[0] - endpos[0]) == 1
            and abs(startpos[0] - self.advanced2_pos[0]) == 1
            and endpos[0] == self.advanced2_pos[0])

  def castling_requirements(
      self, piece: pieces.Piece, endpos: Position, side: Literal[0, 1], gameboard: Board,
      can_castling: 'dict[Color, list[bool]]',
  ):
    '''
    キャスリングの条件を満たすとき，True
    side == 0 -> aファイル側
    side == 1 -> hファイル側

    Parameters
    ----------
    piece : Piece
      駒．キングでなければ Returns は False．
    endpos : tuple > (int, int)
      終了位置．絶対座標．
    side : int > 0, 1
      0 -- クイーンサイド
      1 -- キングサイド
    gameboard : dict > {(int, int): obj, ...}
      盤面．
    can_castling : dict > {'W': [bool, bool], 'B': [bool, bool]}
      キャスリングのポテンシャルが残っているか．

    Returns
    -------
    : bool
    '''
    assert self.kind is not None
    assert self.rook_init_pos is not None
    assert self.king_init_pos is not None
    size = self.kind['size']

    def condition_req(target: Position):
      '''
      target : Position
        キングがキャスリング後到着すべき位置
      '''
      assert self.kind is not None
      assert self.king_init_pos is not None

      # キングが通過するマスが敵に攻撃されていない
      for pos in ((x, 0 if piece.color == 'W' else size - 1)
                  for x in utils.castling_king_route(self.king_init_pos, size=size)[side]):
        _gameboard_tmp = utils.create_tmp_board(gameboard, (self.king_init_pos, endpos[1]), pos)
        if list(self.can_see_square(next(position
                                         for position, pc in _gameboard_tmp.items()
                                         if pc.name == f'{piece.color}K'),
                                    [(position, pc)
                                     for position, pc in _gameboard_tmp.items()
                                     if pc.color == opponent[piece.color]],
                                    _gameboard_tmp)):
          return False

      return (endpos == target
              # キングとルークの通過するマスに駒がない
              and utils.castling_passable(
                  cast(Placers, self.kind['placers']), size, piece.color, side, gameboard))

    # キャスリングに関与する駒が一度も動いていない
    # キングがチェックされていない
    common_req = (can_castling[piece.color][side]
                  and not self.is_check(piece.color, gameboard))
    if not common_req:
      return False

    # 白のキャスリング
    if piece.color == 'W':
      piece_req = (piece.name == 'WK'
                   and (self.rook_init_pos[side], 0) in gameboard
                   and gameboard[(self.rook_init_pos[side], 0)].name == 'WR')
      if not piece_req:
        return False

      # クイーンサイド
      if side == 0:
        return condition_req((2, 0))
      # キングサイド
      elif side == 1:
        return condition_req((size - 2, 0))
    # 黒のキャスリング
    elif piece.color == 'B':
      piece_req = (piece.name == 'BK'
                   and (self.rook_init_pos[side], size - 1) in gameboard
                   and gameboard[(self.rook_init_pos[side], size - 1)].name == 'BR')
      if not piece_req:
        return False

      # クイーンサイド
      if side == 0:
        return condition_req((2, size - 1))
      # キングサイド
      elif side == 1:
        return condition_req((size - 2, size - 1))

    return False

  def castle_or_not(self, piece: pieces.Piece, endpos: Position):
    '''
    キャスリングするかしないかを確認するか

    Parameters
    ----------
    piece : Piece
      駒．
    endpos : Position
      終了位置．絶対座標．

    Notes
    -----
    if文の条件式について．

    キングの移動終了位置が，キャスリング終了位置としてありうる4つの位置のうちのいずれかにあてはまる
      and (クイーンサイドキャスリングの条件にあてはまる
        or キングサイドキャスリングの条件にあてはまる)
      and キングの初期位置とキャスリング終了位置のx座標の差 == 1
      and 移動先に駒がない（＝キングが敵駒を取ったのではない）
    '''
    assert self.kind is not None
    assert self.king_init_pos is not None
    _size = self.kind['size']
    self.do_castling = False
    if (endpos in [(2, 0), (_size - 2, 0), (2, _size - 1), (_size - 2, _size - 1)]
            and (self.castling_requirements(piece, endpos, 0, self.gameboard, self.can_castling)
                 or self.castling_requirements(piece, endpos, 1, self.gameboard, self.can_castling))
            and abs(self.king_init_pos - endpos[0]) == 1
            and endpos not in self.gameboard):
      self.confirm_castling = True
    else:
      self.do_castling = True

  def promotion(self, piece: pieces.Piece, endpos: Position):
    '''
    プロモーションできるとき，prom を True に

    Parameters
    ----------
    piece : Piece
      駒．
    endpos : Position
      終了位置．
    '''
    assert self.kind is not None
    if (piece.name == 'WP' and endpos[1] == self.kind['size'] - 1
            or piece.name == 'BP' and endpos[1] == 0):
      self.prom = True

  def can_see_square(
      self, pos: Position, piecelist: 'list[tuple[Position, pieces.Piece]]', gameboard: Board
  ):
    '''
    pos が piecelist[(position, piece)] の中の
    どれかの駒に攻撃されているとき，攻撃している駒を返す．
    return ではなく yield で返すため，
    攻撃する駒が存在するかどうかは list() を用いて判定する．
    e.g. if list(can_see_square(...)): ...

    Parameters
    ----------
    pos : Position
    piecelist : list > [(Position, Piece), ...]
    gameboard : Board
      盤面．

    Yields
    -------
    piece : Piece
      攻撃している駒．
    '''
    assert self.kind is not None
    for position, piece in piecelist:
      if hasattr(piece, 'archer_dir'):
        arrow_targets: PositionSet = set()
        for moved_pos in piece.available_moves(*position, gameboard, size=self.kind['size']):
          if moved_pos not in gameboard:
            arrow_targets |= utils.arrow_targets_(
                piece, position, moved_pos, gameboard, pu.rider)
        if pos in arrow_targets:
          yield piece
      else:
        if pos in piece.available_moves(*position, gameboard, size=self.kind['size']):
          yield piece

  def is_check(self, color: Color, gameboard: Board):
    '''
    color側がgameboard上でチェックされているとき，True

    Parameters
    ----------
    color : Color
      駒色．
    gameboard : Board
      盤面．

    Returns
    -------
    : bool
    '''
    if (color == 'W'
            and list(self.can_see_square(next(position for position, piece in gameboard.items() if piece.name == 'WK'),
                                         [(position, piece) for position, piece in gameboard.items(
                                         ) if piece.color == 'B'],
                                         gameboard))):
      return True
    if (color == 'B'
            and list(self.can_see_square(next(position for position, piece in gameboard.items() if piece.name == 'BK'),
                                         [(position, piece) for position, piece in gameboard.items(
                                         ) if piece.color == 'W'],
                                         gameboard))):
      return True
    return False

  def cannot_move(self, color: Color):
    '''
    color側が駒を動かすことができないとき，True

    Parameters
    ----------
    color : Color
      駒色．

    Returns
    -------
    : bool
    '''
    # 相手の番である
    if self.playersturn == color:
      for position, piece in self.gameboard.items():
        if color == piece.color:
          for dest in self.valid_moves(piece, position):
            gameboard_tmp = copy(self.gameboard)
            self.renew_gameboard(
                position, dest, gameboard_tmp, color)
            # 自分の駒のどれかをなんらかの形で動かしてチェックされている状態を解除できるなら False
            if not self.is_check(color, gameboard_tmp):
              return False
      # どうあがいてもチェックされた状態を解除できないなら True
      return True
    return False

  def is_stalemate(self, color: Color):
    '''
    color側がステイルメイトになっているとき，True

    Parameters
    ----------
    color : Color
      駒色．

    Returns
    -------
    : bool
    '''
    # 自分の番である
    # 動いたらチェックになるので動けない
    # チェックされているわけでもない
    if (self.playersturn == color
            and self.cannot_move(color)
            and not self.is_check(color, self.gameboard)):
      return True
    return False

  def renew_gameboard(self, startpos: Position, endpos: Position, gameboard: Board, color: Color):
    '''盤面の更新

    Parameters
    ----------
    startpos, endpos : Position
      開始位置，終了位置．絶対座標．
    gameboard : Board
      盤面．
    color : Color
      駒色．
    '''
    assert self.kind is not None
    # 通常の動き
    gameboard[endpos] = copy(gameboard[startpos])
    if startpos != endpos:
      del gameboard[startpos]
    # アンパッサン
    if self.en_passant:
      try:
        advanced2_pos = self.advanced2_record.get(self.count, (None, None))
        # 2歩進んだ人のx位置が、アンパッサン後のアンパッサンしたポーンのx位置に等しい
        if advanced2_pos[0] == endpos[0]:
          assert advanced2_pos[1] is not None
          if color == 'W':
            if (advanced2_pos[1] + 2 == endpos[1] + 1):
              del gameboard[(endpos[0], endpos[1] - 1)]
          if color == 'B':
            if (advanced2_pos[1] - 2 == endpos[1] - 1):
              del gameboard[(endpos[0], endpos[1] + 1)]
      except KeyError:
        pass
    # キャスリング
    # キャスリングできるゲームである
    if self.kind['castling']:
      # キャスリング確認でキャスリングすることを選択した
      # 終了位置指定がある
      if self.do_castling and self.endpos is not None:
        assert self.rook_init_pos is not None
        _size = self.kind['size']
        # クイーンサイド
        if self.castling_requirements(gameboard[endpos], endpos, 0, self.record[self.count], self.can_castling_tmp):
          rook_pos = self.rook_init_pos[0]
          # 白
          if (self.endpos == (2, 0)
                  and self.gameboard[self.endpos].color == 'W'
                  and (rook_pos, 0) in self.gameboard):
            if self.gameboard[(rook_pos, 0)].abbr == 'R':
              del self.gameboard[(rook_pos, 0)]
            self.gameboard[(3, 0)] = pieces.Rook('W')
            self.finish_castling['W'] = self.count
          # 黒
          if (self.endpos == (2, _size - 1)
                  and self.gameboard[self.endpos].color == 'B'
                  and (rook_pos, _size - 1) in self.gameboard):
            if self.gameboard[(rook_pos, _size - 1)].abbr == 'R':
              del self.gameboard[(rook_pos, _size - 1)]
            self.gameboard[(3, _size - 1)] = pieces.Rook('B')
            self.finish_castling['B'] = self.count
        # キングサイド
        if self.castling_requirements(gameboard[endpos], endpos, 1, self.record[self.count], self.can_castling_tmp):
          rook_pos = self.rook_init_pos[1]
          # 白
          if (self.endpos == (_size - 2, 0)
                  and self.gameboard[self.endpos].color == 'W'
                  and (rook_pos, 0) in self.gameboard):
            if self.gameboard[(rook_pos, 0)].abbr == 'R':
              del self.gameboard[(rook_pos, 0)]
            self.gameboard[(_size - 3, 0)] = pieces.Rook('W')
            self.finish_castling['W'] = self.count
          # 黒
          if (self.endpos == (_size - 2, _size - 1)
                  and self.gameboard[self.endpos].color == 'B'
                  and (rook_pos, _size - 1) in self.gameboard):
            if self.gameboard[(rook_pos, _size - 1)].abbr == 'R':
              del self.gameboard[(rook_pos, _size - 1)]
            self.gameboard[(_size - 3,
                            _size - 1)] = pieces.Rook('B')
            self.finish_castling['B'] = self.count

  def refresh_memo(self, board: 'Optional[Board]' = None):
    # 駒の動きのメモを初期化
    assert self.kind is not None
    board_is_none = False
    if board is None:
      board_is_none = True
      board = self.gameboard
    for pos, piece in board.items():
      if board_is_none:
        piece.recalc = True
      if type(piece) is Orphan or type(piece) is Friend:
        piece.tmp_moves = set()
        piece.tmp_potentials = set()
        piece.res_potentials = set()
        piece.compounded_normal_pieces_memo = None
    for pos, piece in board.items():
      if type(piece) is Orphan or type(piece) is Friend:
        piece.give_moves(*pos, board, self.kind['size'])

  def process_after_renewing_board(self):
    '''駒を動かしたあとの処理'''
    assert self.kind is not None
    assert self.endpos is not None
    piece = self.gameboard[self.endpos]
    if not (self.prom or self.confirm_castling or self.arrow_targets):
      # ターン交代
      self.playersturn = opponent[self.playersturn]
      # 動きの記録
      self.record[self.count + 1] = deepcopy(self.gameboard)
      self.count += 1
      # 駒の動きのメモを初期化
      self.refresh_memo()
    # チェック状態の記録
    self.check_bool = self.is_check(
        'W', self.gameboard) or self.is_check('B', self.gameboard)
    self.stalemate_bool = self.is_stalemate('W') or self.is_stalemate('B')
    self.checkmate_bool = self.cannot_move('W') or self.cannot_move('B')
    # プロモーション(CPU)
    if (self.prom
            and self.mode == 'PvsC'
            and self.playersturn != self.my_color):
      self.prom = False
      self.process_after_renewing_board()
      self.gameboard[self.endpos] = self.kind['promote2'][-1](piece.color)
      return
    # 動きの上書き
    len_record = len(self.record)
    last_record = list(self.record.keys())[-1]
    if len_record - 1 != last_record:
      for i in range(len_record, last_record):
        del self.record[i]
    # 回数によって動きが変わる駒が何手目でどこの駒が何回動いたか記録する
    if hasattr(piece, 'count'):
      self.move_record[self.count] = self.endpos
    # 何手目でどこのポーンが2歩進んだか記録する
    if self.advanced2_pos:
      self.advanced2_record[self.count] = self.advanced2_pos
    elif self.count in self.advanced2_record.keys():
      del self.advanced2_record[self.count]
    # 何手目でどちらのどこのキャスリングの可能性がなくなったか記録する
    if self.can_castling != self.can_castling_tmp:
      status = tuple((k, i)
                     for k, v in self.can_castling.items()
                     for i in (0, 1)
                     if v[i] != self.can_castling_tmp[k][i])
      self.give_up_castling[self.count] = cast(
          Tuple[Tuple[Color, Literal[0]], Tuple[Color, Literal[1]]], status)

  def prev_move(self):
    '''一手戻す'''
    self.count -= 1
    if self.count < 0:
      self.count = 0
      self.playersturn = opponent[self.playersturn]
    self.gameboard = deepcopy(self.record[self.count])
    self.playersturn = opponent[self.playersturn]
    # 駒の動きのメモを初期化
    self.refresh_memo()
    # ポーンが2歩進んだ直後であるとき
    for k in self.advanced2_record:
      if self.count == k:
        self.advanced2_pos = self.advanced2_record[k]
    # キャスリング
    for color, count in self.finish_castling.items():
      if count == self.count:
        self.finish_castling_tmp[color] = count
        self.finish_castling[color] = 0
    for k in self.give_up_castling:
      if self.count == k - 1:
        for i in range(len(self.give_up_castling[k])):
          self.can_castling[
              self.give_up_castling[k][i][0]][self.give_up_castling[k][i][1]] = True
    self.startpos, self.endpos = None, None

  def next_move(self):
    '''一手進める'''
    self.count += 1
    if self.count > len(self.record) - 1:
      self.count = len(self.record) - 1
      self.playersturn = opponent[self.playersturn]
    self.gameboard = deepcopy(self.record[self.count])
    self.playersturn = opponent[self.playersturn]
    # 駒の動きのメモを初期化
    self.refresh_memo()
    # ポーンが2歩進んだ直後であるとき
    for k in self.advanced2_record.keys():
      if self.count == k:
        self.advanced2_pos = self.startpos
    # キャスリング
    for color, count in self.finish_castling_tmp.items():
      if count == self.count:
        self.finish_castling[color] = count
    for k in self.give_up_castling.keys():
      if self.count == k:
        for i in range(len(self.give_up_castling[k])):
          self.can_castling[self.give_up_castling[k][i]
                            [0]][self.give_up_castling[k][i][1]] = False
    self.startpos, self.endpos = None, None

  def load_data(self):
    '''ゲームデータのロード'''
    import load_data
    data = load_data.data
    self.kind = data['game']
    self.mode = data['mode']
    self.level = data['level']
    self.foreseeing = data['foreseeing']
    self.gameboard = data['gameboard']
    self.playersturn = data['playersturn']
    self.move_record = data['move_record']
    self.advanced2_pos = data['advanced2_pos']
    self.advanced2_record = data['advanced2_record']
    self.can_castling = data['can_castling']
    self.count = data['count']
    self.record = data['record']
    # ルーク・キングの初期位置の記録
    if self.kind['castling']:
      self.rook_init_pos = utils.rook_init_pos(cast(Placers, self.kind['placers']))
      self.king_init_pos = utils.king_init_pos(cast(Placers, self.kind['placers']))
