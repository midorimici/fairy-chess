## 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## 起動方法

ルートディレクトリで次のコマンドを打つ。

ゲームを起動するとき

- `./chess`(シェルスクリプト)
- `chess`(コマンドプロンプト)

辞書を起動するとき

- `./chess -d`(シェルスクリプト)
- `chess d`(コマンドプロンプト)

## ゲーム種追加・編集方法

`codes/main/games` 以下の `yml` ファイルに以下のように定義する。

```yml
# 表示名
name: Normal Chess
# 盤面サイズ
size: 8
# キャスリングの有無
castling: true
# ポーンのプロモーション先
promote2:
  - Knight
  - Bishop
  - Rook
  - Queen
# 非対称ゲームか。true にすると、placers では白から 1 -> 8 で非対称な盤面を設定できる。
asym: false
# 初期配置。1 が最手前側。
placers:
  1: [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
  2: [Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn]
```

## フェアリー駒追加方法

1. `fairy_pieces` のいずれかに新クラスを定義(2 は Noble Chess 用，3 は外因によって動きが変わったり周囲の動きを変えたりする特殊な駒)

1. `dict/pieces.yml` にクラス名を追加

1. クラスの `abbr` 属性の先頭に `'W'` をつけた名前で `assets/img/W` に，`'B'` をつけた名前で `assets/img/B` に，100x100 のサイズの駒の画像を作成

1. `assets/img/dict` に，クラス名の先頭に `'exp'` をつけた名前で駒の説明画像を作成
