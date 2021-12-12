'''駒関連の関数の定義'''

from math import floor, sqrt
from typing import Literal
import numpy as np
import re

from custom_types import PositionList, PositionSet, Board, Color
from utils import move_list, in_zone


king_move: PositionList = [(0, 1), (1, 1), (1, 0), (1, -1),
                           (0, -1), (-1, -1), (-1, 0), (-1, 1)]


def is_in_bounds(x: int, y: int, size: int = 14):
  '''
  盤面の上に駒があるかどうか
  デフォルト値にはありうる最大のsize=14を指定

  Parameters
  ----------
  x, y : int
    駒の絶対座標．
  size : int
    盤面の大きさ．

  Returns
  -------
  : bool
    盤面の上に駒がある場合True
  '''
  if 0 <= x < size and 0 <= y < size:
    return True
  return False


def no_conflict(gameboard: Board, color: Color, x: int, y: int, size: int = 14, move_only: bool = False):
  '''
  盤面の外に出ていかない　かつ　（行先に駒がない　または　行先の駒色が自分と異なる）

  Parameters
  ----------
  gameboard : Board
    盤面．
  color : Color
    駒色．
  x, y : int
    駒の絶対座標．
  size : int
    盤面の大きさ．
  move_only : bool, default False
    True のとき，相手の駒を取ることができない．

  Returns
  -------
  : bool
  '''
  if (is_in_bounds(x, y, size)
      and (((x, y) not in gameboard)
           or ((gameboard[(x, y)].color != color)
           if not move_only else False))):
    return True
  return False


def dir8(x: int, y: int) -> PositionList:
  '''
  (x, y)をx軸, y軸, 直線y=xに関して対称移動させたものを追加
  (x, y)-leaper 方向

  Parameters
  ----------
  x, y : int
    移動の方向．

  Returns
  -------
  List[Position]
    移動の方向のリスト．時計回り．要素数8．
  '''
  return [(x, y), (y, x), (y, -x), (x, -y),
          (-x, -y), (-y, -x), (-y, x), (-x, y)]


def dist_dir(dist: int, sep: bool = False):
  '''
  原点からの距離が dist の位置(相対座標)を出力

  Parameters
  ----------
  dist : int
    原点からの距離．
  sep : bool
    出力形式を変更する．Returnsを参照のこと．

  Returns
  -------
  if sep:
    List[PositionSet]
  else:
    PositionSet

  See Also
  --------
  PrimeLeaper など， MathChess に登場する駒
  '''
  if sep:
    return [dir8(i, j)
            for i in range(floor(sqrt(dist) * sqrt(2) / 2) + 1)
            for j in range(floor(sqrt(dist) * sqrt(2) / 2), floor(sqrt(dist)) + 1)
            if i**2 + j**2 == dist]
  return sum([dir8(i, j)
              for i in range(floor(sqrt(dist) * sqrt(2) / 2) + 1)
              for j in range(floor(sqrt(dist) * sqrt(2) / 2), floor(sqrt(dist)) + 1)
              if i**2 + j**2 == dist], [])


def _notation_o(
    symbol: str, storage_notations: str, first: 'list[PositionList]', second: PositionList
) -> 'list[PositionList]':
  '''
  moves_from で使う．
  o(A)と表記があれば，first から見て外側の second の移動先を出力．

  Parameters
  ----------
  symbol : str
    解析する文字列．
  storage_notations : str
    変数として moves_from の引数 storage に格納されている文字列．
  first : list[PositionList]
    A>B と書かれたときの A の動き.
  second : PositionList
    A>B と書かれたときの B の動き.

  Returns
  -------
  list[PositionList]
    first から見て外側の second の移動先．
  '''
  if (re.search(r'^o\(.+?\)$', symbol)
          or re.search(r'^o\(.+?\)$', storage_notations)):
    # first と second のそれぞれのベクトルの内積が正の値をとる
    # = ベクトルのなす角が90°より小さい
    return [[vec2
            for vec2 in second
            if np.asarray(vec1[0]) @ np.asarray(vec2) > 0]
            for vec1 in first]
  else:
    return [second] * len(first)


def _notation_m(symbol: str, storage_notations: str, func, args) -> PositionSet:
  '''
  moves_from で使う．
  m(A)と表記があれば，移動のみで攻撃はできないようにする．

  Parameters
  ----------
  symbol : str
    解析する文字列．
  storage_notations : str
    変数として moves_from の引数 storage に格納されている文字列．
  func : function
    駒の種類を指定．rider, leaper など．
  args : tuple
    func の引数．

  Returns
  -------
  PositionSet
      駒の可能な移動先．
  '''
  if (re.search(r'^m\(.+?\)$', symbol)
          or re.search(r'^m\(.+?\)$', storage_notations)):
    return func(*args, move_only=True)
  else:
    return func(*args)


def moves_from(
    notation: str, x: int, y: int, gameboard: Board, color: Color,
    size: int = None, relative: bool = False, **storage: str,
) -> PositionSet:
  '''
  notation をもとに動きを出力．

  Parameters
  ----------
  notation : str
    動きを表したもの．
    ',' で区切られた文字列で表された動きが合わさる．
  x, y : int
    駒の絶対座標．
  gameboard : Board
    盤面．
  color : Color
    駒色．
  size : int
    盤面のサイズ．
  relative : bool
    True のとき，相対座標(方向)を出力．
  storage : dict > {str: str}
    変数として使う．

  Returns
  -------
  output : PositionSet
    駒の可能な移動先．

  Notes
  -----
  notation について．([n], [m] は任意の整数，[N] は任意の自然数)

  - +       十字方向
  - x       斜め方向
  - [n]/[m] 白から見て駒から右に[m], 前に[n]
  - **A     A の動きを8方向に(dir8(A))
  - A,B     A と B をあわせたもの
  - A_      A の動きを一直線にする(rider)
  - [N]A    A の動きを[N]倍に拡大する
  - A[N]    A 方向の動きを[N]回までする(rider. length=N)
  - m(A)    A の動きでは敵駒を取れない
  - c(A)    A の動きでは敵駒を取らないといけない
  - A>B     A の動きをしてから B の動きをする( A は含まない)
  - o(A)    A の動きの駒から見て外側の部分に

  Examples
  --------
  '+,x' : King
  '**2/1' : Knight
  '2+,2x' : Knightess
  '+2' : Mist
  'x_' : Bishop
  'K>o(**2/1)', 'K'='+,x' : Count
  '+>x_, x_>+, x_, +' : GrandDuke
  '''
  common_args = x, y, gameboard, color
  output: PositionSet = set()
  for symbol in notation.split(','):
    # 段階的な動きであるとき
    if '>' in symbol:
      first, second = symbol.split('>')
      first_move, second_move = \
          (moves_from(first, *common_args, relative=True, **storage),
           moves_from(second, *common_args, relative=True, **storage))
      # first_move の構造を変更
      first_move_list: 'list[PositionList]' = [[pos] for pos in first_move]
      # > の前に使われている変数の中で storage に格納されている文字列
      storage_notations = ''.join(storage[name] for name in storage if name in first)
      # > の前に A_ の有無
      rider_symbol = re.search(r'[a-z]?\(?(.+?)\)?_\)?', storage_notations + first)
      if rider_symbol:
        if size is None:
          raise TypeError('available_moves > moves_from の引数に size が指定されていません．')
        first_move_list = [[(i * x, i * y) for i in range(1, size)]
                           for [(x, y)] in first_move_list]
      # > の後に使われている変数の中で storage に格納されている文字列
      storage_notations = ''.join(storage[name] for name in storage if name in second)
      # > の後に A_ の有無
      rider_symbol = re.search(r'[a-z]?\(?(.+?)\)?_\)?', storage_notations + second)
      if rider_symbol:
        rider_move = moves_from(rider_symbol.group(1), *common_args,
                                relative=True, **storage)
        # o(A)
        rider_move = _notation_o(second, storage_notations,
                                 first_move_list, list(rider_move))
        # slide rider
        output |= slide_rider(*common_args,
                              first_move_list, rider_move)
      else:
        # 末尾の数字の有無
        rider_symbol = re.search(r'[a-z]?\(?(.*?[^*/])\)?(\d+)\)?', storage_notations + second)
        if rider_symbol:
          rider_move = moves_from(rider_symbol.group(1), *common_args,
                                  relative=True, **storage)
          # o(A)
          rider_move = _notation_o(second, storage_notations,
                                   first_move_list, list(rider_move))
          foot_num = int(rider_symbol.group(2))
          # length つき slide rider
          output |= slide_rider(*common_args,
                                first_move_list, rider_move,
                                length=foot_num)
        else:
          leaper_move = _notation_o(second, storage_notations,
                                    first_move_list, list(second_move))
          # slide leaper
          if size is None:
            raise TypeError('available_moves > moves_from の引数に size が指定されていません．')
          output |= slide_leaper(*common_args, size,
                                 first_move_list, leaper_move)

    # 屈折のない動きであるとき
    else:
      direction: PositionList = []
      # 変数
      storage_notations = ''
      for name in storage:
        if name in symbol:
          storage_notations = storage[name]
          direction = list(moves_from(
              storage_notations, *common_args, relative=True, **storage))

      # 単体で動きを表すもの
      vector = re.search(r'-?\d+/-?\d+', symbol)
      # '+' で十字方向
      if '+' in symbol:
        direction = dir8(0, 1)
      # 'x' で斜め方向
      elif 'x' in symbol:
        direction = dir8(1, 1)
      # [n]/[m] ベクトル指定
      elif vector:
        n, m = map(int, vector.group().split('/'))
        direction = [(m, n)]

      # 装飾子
      # **A
      if re.search(r'\(?\*\*', symbol):
        direction = dir8(*direction[0])
      # A_ : rider
      if (re.search(r'.+?_\)?$', symbol)
              or re.search(r'.+?_\)?$', storage_notations)):
        tmp = _notation_m(symbol, storage_notations,
                          rider, (*common_args, direction, size, None, False,
                                  gameboard[(x, y)].abbr in ('Mi', 'Bz')))
      else:
        # 数字つき([n]/[m] はのぞく)
        head_num = re.search(r'^([a-z]\()?(\d+)[^/]', symbol)
        foot_num = (re.search(r'[^/](\d+)\)?$', symbol)
                    or re.search(r'[^/](\d+)\)?$', storage_notations))
        # 頭に数字がついている場合
        if head_num:
          direction = [(xx, yy)
                       for xx, yy in (int(head_num.group(2)) * (np.asarray(direction))).tolist()]
          tmp = _notation_m(symbol, storage_notations,
                            leaper, (*common_args, direction, size if size is not None else 14))
        # 末尾に数字がついている場合 : length つき rider
        elif foot_num:
          tmp = _notation_m(symbol, storage_notations,
                            rider, (*common_args, direction, size, int(foot_num.group(1)), False,
                                    gameboard[(x, y)].abbr in ('Mi', 'Bz')))
        else:
          # leaper
          tmp = _notation_m(symbol, storage_notations,
                            leaper, (*common_args, direction, size if size is not None else 14))
      # c(A)
      if (re.search(r'^c\(.+?\)$', symbol)
              or re.search(r'^c\(.+?\)$', storage_notations)):
        tmp: PositionSet = {pos for pos in tmp
                            if (pos in gameboard and no_conflict(gameboard, color, *pos, size=size or 14))}
      if relative:
        tmp = set(direction)
      output |= tmp
  return output


def leaper(
    x: int, y: int, gameboard: Board, color: Color, direction: PositionList,
    size: int, move_only: bool = False
) -> PositionSet:
  '''
  跳び駒の移動先を出力．
  駒の位置や色，盤面の状態から，
  相対座標(方向 : direction)を絶対座標に変換する．

  Parameters
  ----------
  x, y : int
    駒の位置．
  gameboard : Board
    盤面．
  color : Color
    駒色．
  direction : PositionList
    駒の移動方向．
  size : int
    盤面のサイズ．
  move_only : bool, default False
    True のとき，相手の駒を取ることができない．


  Returns
  -------
  PositionSet
    駒の可能な移動先．
  '''
  return {(xx, yy) for xx, yy in move_list((x, y), set(direction))
          if no_conflict(gameboard, color, xx, yy, size=size, move_only=move_only)}


def rider(
    x: int, y: int, gameboard: Board, color: Color, intervals: PositionList,
    size: int = 14, length: int = None, move_only: bool = False, is_mist: bool = False,
) -> PositionSet:
  '''
  与えられた座標への移動を一直線にする．走り駒，ユニコーンなど用．
  相対座標(方向 : intervals)を絶対座標に変換する．

  Parameters
  ----------
  x, y : int
    駒の絶対座標．
  gameboard : Board
    盤面．
  color : Color
    駒色．
  intervals : PositionList
    移動の方向．相対座標．
  size : int
    盤面の大きさ．
  length : int or None, default None
    intervalsの方向に移動する最大の回数．
  move_only : bool, default False
    Trueのとき，移動によって相手の駒を取ることができない．
  is_mist : bool
    自分がミストやブリザードなど霧系の駒か．

  Returns
  -------
  answers : PositionSet
    駒の可能な移動先．

  See Also
  --------
  Rook, Bishop :
    length, move_only 不使用．
  Tank :
    move_only 使用．
  Mist :
    length 使用．
  '''
  answers: PositionSet = set()
  for xint, yint in set(intervals):
    # intervals 中の (xint, yint) 方向について
    # (xtemp, ytemp) : 盤面上の現在位置絶対座標 (x, y) から (xint, yint) 方向に動いたときの絶対座標
    xtemp, ytemp = x + xint, y + yint
    # condition : length の指定なし(None)の場合，盤面上に収まること．
    #   指定ありの場合，その回数以内の移動であること．
    condition = (is_in_bounds(xtemp, ytemp, size) if length is None
                 else (abs(x - xtemp) <= abs(xint) * length
                       and abs(y - ytemp) <= abs(yint) * length))
    while condition:
      # target : 盤面上の (xtemp, ytemp) の位置に駒があればその駒(obj)．
      #   なければ None．
      target = gameboard.get((xtemp, ytemp))
      if target is None:
        # 駒がないのでそのマスには動ける
        answers.add((xtemp, ytemp))
        if ((in_zone(gameboard, 2, (xtemp, ytemp), 'Mi')
             or in_zone(gameboard, 1, (xtemp, ytemp), 'Bz'))
                and not is_mist):
          # ミストorブリザードにぶつかったので，そこで止まる
          break
      elif target.color != color and not move_only:
        # 相手の駒があり，その移動で取ることができるので，取れる
        answers.add((xtemp, ytemp))
        # 駒にぶつかったので，これ以上進めない
        break
      else:
        # 自分の駒にぶつかったので，これ以上進めない
        break

      # (xtemp, ytemp) から (xint, yint) 方向に一回動く
      xtemp += xint
      ytemp += yint
      # condition の更新
      condition = (is_in_bounds(xtemp, ytemp, size) if length is None
                   else (abs(x - xtemp) <= abs(xint) * length
                         and abs(y - ytemp) <= abs(yint) * length))
  return answers


def wave_rider(
    x: int, y: int, gameboard: Board, color: Color, intervals: PositionList, size: int,
) -> PositionSet:
  '''
  波うちながら走る．ウェーブ用

  Parameters
  ----------
  x, y : int
    駒の絶対座標．
  gameboard : Board
    盤面．
  color : Color
    駒色．
  intervals : PositionList
    移動の方向．相対座標．
  size : int
    盤面の大きさ．

  Returns
  -------
  answers : PositionSet
    駒の可能な移動先．

  See Also
  --------
  Wave :
    intervals -- dir8(1, 1)
  Horse :
    intervals -- dir8(1, 2)
  Donkey :
    intervals -- dir8(2, 1)
  '''
  answers: PositionSet = set()
  # (xtemp, ytemp) は絶対座標
  for xtemp, ytemp in move_list((x, y), {(xx, yy) for xx, yy in intervals if abs(xx) == intervals[0][0]}):
    var = 0
    # 前後方向への波
    while is_in_bounds(xtemp, ytemp, size):
      target = gameboard.get((xtemp, ytemp))
      if target is None:
        # 駒がないのでそのマスには動ける
        answers.add((xtemp, ytemp))
        if (in_zone(gameboard, 2, (xtemp, ytemp), 'Mi')
                or in_zone(gameboard, 1, (xtemp, ytemp), 'Bz')):
          # ミストorブリザードにぶつかったので，そこで止まる
          break
      elif target.color != color:
        answers.add((xtemp, ytemp))
        break
      else:
        break
      # 移動先が駒より左側
      if xtemp < x:
        var = intervals[0][0]
      # 移動先が駒より右側
      elif xtemp > x:
        var = -intervals[0][0]
      # 次の移動先
      xtemp += var
      # 前方向に進んでいるなら前へ，後ろなら後ろへ
      ytemp += intervals[0][1] if ytemp > y else -intervals[0][1]
  for xtemp, ytemp in move_list((x, y), {(xx, yy) for xx, yy in intervals if abs(yy) == intervals[0][0]}):
    var = 0
    # 左右方向への波
    while is_in_bounds(xtemp, ytemp, size):
      target = gameboard.get((xtemp, ytemp))
      if target is None:
        answers.add((xtemp, ytemp))
      elif target.color != color:
        answers.add((xtemp, ytemp))
        break
      else:
        break
      # 移動先が駒より白側
      if ytemp < y:
        var = intervals[0][0]
      # 移動先が駒より黒側
      elif ytemp > y:
        var = -intervals[0][0]
      # 次の移動先
      ytemp += var
      # 右方向に進んでいるなら右へ，左なら左へ
      xtemp += intervals[0][1] if xtemp > x else -intervals[0][1]
  return answers


def reflect_rider(
    x: int, y: int, gameboard: Board, color: Color, intervals: PositionList, ref_num, size
) -> PositionSet:
  '''
  盤面の縁で反射するライダー

  Parameters
  ----------
  x, y : int
    駒の絶対座標．
  gameboard : Board
    盤面．
  color : Color
    駒色．
  intervals : PositionList
    移動の方向．相対座標．
  ref_num : int
    反射する回数．4 回まで
  size : int
    盤面の大きさ．

  Returns
  -------
  answers : PositionSet
    駒の可能な移動先．

  See Also
  --------
  ReflectingBishop :
    intervals -- dir8(1, 1)
  '''
  answers: PositionSet = set()
  for xint, yint in intervals:
    xtemp, ytemp = x + xint, y + yint
    reflect_num = 0  # 反射済回数
    while is_in_bounds(xtemp, ytemp, size) and reflect_num <= ref_num:  # ここの値が何回まで反射できるかを表す
      target = gameboard.get((xtemp, ytemp))
      if target is None:
        # 駒がないのでそのマスには動ける
        answers.add((xtemp, ytemp))
        if (in_zone(gameboard, 2, (xtemp, ytemp), 'Mi')
                or in_zone(gameboard, 1, (xtemp, ytemp), 'Bz')):
          # ミストorブリザードにぶつかったので，そこで止まる
          break
      elif target.color != color:
        answers.add((xtemp, ytemp))
        break
      else:
        break

      # 盤面の縁に到達した
      if xtemp <= 0 or xtemp >= size - 1:
        reflect_num += 1
        xint = -xint
      if ytemp <= 0 or ytemp >= size - 1:
        reflect_num += 1
        yint = -yint
      xtemp += xint
      ytemp += yint
  return answers


def slide_leaper(
    x: int, y: int, gameboard: Board, color: Color, size: int,
    startlist: 'list[PositionList]', dest: 'list[PositionList]', absolute: Literal['dest'] = None
) -> PositionSet:
  '''
  start に駒やミストエリアがないときにのみ dest の方向に跳ぶ

  Parameters
  ----------
  x, y : int
    駒の絶対座標．
  gameboard : Board
    盤面．
  size : int
    盤面の大きさ．
  startlist, dest : List[PositionList]
    startlist の中の特定の方向に駒・ミストエリアがないときにのみ，
    その方向から見て，対応する列の dest の方向に移動することができる．
    e.g. startlist = [[(1, 1), (2, 2)], [(1, -1), (2, -2)], [(-1, -1), (-2, -2)], [(-1, 1), (-2, 2)]]
    dest = [[(0, 1), (1, 0)], [(1, 0), (0, -1)], [(0, -1), (-1, 0)], [(-1, 0), (0, 1)]]
    この場合， (1, 1), (2, 2) のどちらにも駒がないときに限り，
    (2, 2) + (0, 1), (2, 2) + (1, 0) のマスに行けることになる．
    (2, 2) にのみ駒があっても (1, 1) + (0, 1), (1, 1) + (1, 0) には行ける．
  absolute : str > 'dest' or None, default None
    'dest' にすると駒からみた位置で dest を指定する

  Returns
  -------
  : PositionSet
    駒の可能な移動先．

  See Also
  --------
  Esquire :
    startlist -- [[(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]],
    dest -- [[(0, 1), (1, 0)], [(1, 0), (0, -1)], [(0, -1), (-1, 0)], [(-1, 0), (0, 1)]]
  '''
  ans: PositionSet = set()
  if absolute == 'dest':
    for bflist in startlist:
      if all([is_in_bounds(x + posX, y + posY, size)
              and (x + posX, y + posY) not in gameboard
              and not (in_zone(gameboard, 2, (x + posX, y + posY), 'Mi')
                       or in_zone(gameboard, 1, (x + posX, y + posY), 'Bz'))
              for posX, posY in bflist]):
        ans |= leaper(x, y, gameboard, color, dest[startlist.index(bflist)], size)
  else:
    for bflist in startlist:
      for start in bflist:
        # それまでのすべてのマスについて，
        # 盤面上にあり，駒がなく，ミストエリアでない場合
        if all([is_in_bounds(x + posX, y + posY, size)
                and (x + posX, y + posY) not in gameboard
                and not (in_zone(gameboard, 2, (x + posX, y + posY), 'Mi')
                         or in_zone(gameboard, 1, (x + posX, y + posY), 'Bz'))
                for posX, posY in bflist[:(bflist.index(start) + 1)]]):
          ans |= leaper(x, y, gameboard, color, list(move_list(start, set(dest[startlist.index(bflist)]))), size)
  return ans


def slide_rider(
    x: int, y: int, gameboard: Board, color: Color,
    startlist: 'list[PositionList]', dest: 'list[PositionList]', length: int = None, size: int = 14
) -> PositionSet:
  '''
  start に駒がないときにのみ dest の方向に走る

  Parameters
  ----------
  x, y : int
    駒の絶対座標．
  gameboard : Board
    盤面．
  startlist, dest : List[PositionList]
    startlist の中の特定の方向に駒がないときにのみ，
    その方向から見て，対応する列の dest の方向に走ることができる．
    e.g. startlist = [[(0, 1)], [(1, 0)], [(0, -1)], [(-1, 0)]]
    dest = [[(-1, 1), (1, 1)], [(1, 1), (1, -1)], [(1, -1), (-1, -1)], [(-1, -1), (-1, 1)]]
    この場合， (0, 1) に駒がないときに限り，
    (0, 1) から (-1, 1) または (1, 1) の方向に走れることになる．
  length : int or None, default None
    dest の方向に移動する最大の回数．
  size : int
    盤面の大きさ．

  Returns
  -------
  : PositionSet
    駒の可能な移動先．

  See Also
  --------
  Griffin :
    startlist -- [[(1, 1)], [(1, -1)], [(-1, -1)], [(-1, 1)]],
    dest -- [[(0, 1), (1, 0)], [(1, 0), (0, -1)], [(0, -1), (-1, 0)], [(-1, 0), (0, 1)]]
  Marquis :
    startlist -- [[(1, 2)], [(2, 1)], [(2, -1)], [(1, -2)],
        [(-1, -2)], [(-2, -1)], [(-2, 1)], [(-1, 2)]],
    dest -- [[(0, 1), (1, 0)], [(0, 1), (1, 0)],
            [(1, 0), (0, -1)], [(1, 0), (0, -1)],
            [(0, -1), (-1, 0)], [(0, -1), (-1, 0)],
            [(-1, 0), (0, 1)], [(-1, 0), (0, 1)]],
    length -- 2
  '''
  ans: PositionSet = set()
  for bflist in startlist:
    for start in bflist:
      # それまでのすべてのマスについて，
      # 盤面上にあり，駒がなく，ミストエリアでない場合
      if all([is_in_bounds(x + posX, y + posY)
              and (x + posX, y + posY) not in gameboard
              and not (in_zone(gameboard, 2, (x + posX, y + posY), 'Mi')
                       or in_zone(gameboard, 1, (x + posX, y + posY), 'Bz'))
              for posX, posY in bflist[:(bflist.index(start) + 1)]]):
        ans |= rider(x + start[0], y + start[1], gameboard, color,
                     dest[startlist.index(bflist)], size, length=length,
                     is_mist=gameboard[(x, y)].abbr in ('Mi', 'Bz'))
  return ans
