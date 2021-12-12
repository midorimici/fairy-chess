'''数学に関する共通の関数を集めたモジュール'''


from math import floor, sqrt


def is_prime(n: int):
  '''
  n(>=2)が素数であれば True を返す

  Parameters
  ----------
  n : int > 2-
    2以上の任意の自然数．

  Returns
  -------
  : bool
  '''
  if n == 2:
    return True
  if n % 2 == 0:
    return False
  for i in range(3, floor(sqrt(n)) + 1, 2):
    if n % i == 0:
      return False
  return True


def knacci(k: int, n: int):
  '''
  n 番目の k-ナッチ数

  Parameters
  ----------
  n : int > 1-
    任意の自然数．

  Returns
  -------
  : int
  '''
  var = [0] * (k - 1) + [1]
  for i in range(1, k + 1):
    if n == i:
      return var[i - 1]
  for i in range(n - k):
    var = [var[j] for j in range(1, k)] + [sum(var)]
  return var[-1]


def _lucas(n: int):
  '''
  n 番目のリュカ数

  Parameters
  ----------
  n : int > 1-
    任意の自然数．

  Returns
  -------
  : int
  '''
  a, b = 2, 1
  if n == 1:
    return a
  elif n == 2:
    return b
  else:
    for _ in range(n - 2):
      a, b = b, a + b
    return b


def _pell(n: int):
  '''
  n 番目のペル数

  Parameters
  ----------
  n : int > 1-
    任意の自然数．

  Returns
  -------
  : int
  '''
  a, b = 1, 2
  if n == 1:
    return a
  elif n == 2:
    return b
  else:
    for _ in range(n - 2):
      a, b = b, a + 2 * b
    return b


def _perrin(n: int):
  '''
  n 番目のペラン数

  Parameters
  ----------
  n : int > 1-
    任意の自然数．

  Returns
  -------
  : int
  '''
  a, b, c = 3, 0, 2
  if n == 1:
    return a
  elif n == 2:
    return b
  elif n == 3:
    return c
  else:
    for _ in range(n - 3):
      a, b, c = b, c, a + b
    return c


# 42までの素数リスト
primes = [i for i in range(2, 42) if is_prime(i)]

# 15番目までのフィボナッチ数リスト
fibos = [knacci(2, i) for i in range(2, 15)]

# 14番目までのトリボナッチ数リスト
tribos = [knacci(3, i) for i in range(3, 14)]

# 14番目までのテトラナッチ数リスト
tetras = [knacci(4, i) for i in range(4, 14)]

# 14番目までのペンタナッチ数リスト
pentas = [knacci(5, i) for i in range(5, 14)]

# 15番目までのリュカ数リスト
lucas = [_lucas(i) for i in range(1, 15)]

# 8番目までのペル数リスト
pells = [_pell(i) for i in range(1, 8)]

# 23番目までのペラン数リスト
perrins = [_perrin(i) for i in range(3, 23)]
