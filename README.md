# 概要

フェアリーチェスが遊べるアプリケーションです。

ゲームと辞書のふたつがあり、辞書では駒の動きを調べたり動かしてみたりすることができます。

# ガイド

## 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## 起動方法

起動には Python と依存パッケージが必要。

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

# ライセンス

このアプリケーションは、[rsheldiii](https://gist.github.com/rsheldiii) による [chess program for python](https://gist.github.com/rsheldiii/2993225) をベースに変更・機能追加を行ったものです。

駒の画像は [Clker-Free-Vector-Images](https://pixabay.com/ja/users/Clker-Free-Vector-Images-3736/) による [Pixabay](https://pixabay.com/ja/) からの [画像](https://pixabay.com/ja/vectors/%E3%83%81%E3%82%A7%E3%82%B9-%E4%BD%9C%E5%93%81-%E8%A8%AD%E5%AE%9A-%E3%82%B7%E3%83%B3%E3%83%9C%E3%83%AB-26774/) および [Alfaerie Variant Chess Graphics](https://www.chessvariants.com/graphics.dir/alfaerie/index.html) をもとに作成したものに加え、自作のグラフィックも含みます。

駒の説明画像や Notation 説明画像は自作のものです。

効果音素材は [On-Jin ～音人～](https://on-jin.com) のものを使用しています。

フォントは [Cica](https://github.com/miiton/Cica) を使用しています。
