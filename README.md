# J-Quants → MT4 日本株チャート取り込みシステム

## 概要

J-Quants API から日本株の日足OHLCデータを取得し、MT4でローソク足チャートとして扱いやすいCSV形式へ変換するプロジェクトです。

初期検証対象:

- 銘柄コード: 4661
- 銘柄名: オリエンタルランド
- 取得期間: Standardプラン最大範囲を想定
- 更新タイミング: 1日1回 AM7:00
- MT4: XMTrading MT4 build 1470 想定

## 重要

APIキーは絶対にソースコードへ直書きしないでください。

`config/config.example.json` を `config/config.json` にコピーして、そこへ設定してください。

## 推奨構成

- Python: J-Quants API取得・CSV生成
- MT4: CSVを読み込むスクリプト・インディケーター
- Windowsタスクスケジューラ: 毎朝7時の自動更新

## フォルダ構成

```text
config/
  config.example.json
scripts/
  fetch_jquants_v2.py
  normalize_ohlc.py
  update_stock_data.py
  install_to_mt4.py
  update_stock_data.bat
mt4/
  MQL4/
    Scripts/
      JPStock_ImportCsv_OfflineChart.mq4
    Indicators/
      JPStock_CloseLine_FromCsv.mq4
data/
  raw/
  processed/
  mt4_csv/
logs/
docs/
  SETUP_JA.md
```

## 使い方

### 1. Python依存関係のインストール

```bat
pip install -r requirements.txt
```

### 2. 設定ファイル作成

```bat
copy config\config.example.json config\config.json
```

`config/config.json` にJ-Quants APIキー、銘柄コード、MT4フォルダを設定してください。

### 3. データ取得・変換

```bat
python scripts\update_stock_data.py --config config\config.json
```

### 4. MT4へCSVを配置

```bat
python scripts\install_to_mt4.py --config config\config.json
```

### 5. MT4側

MT4の `MQL4/Scripts` に `JPStock_ImportCsv_OfflineChart.mq4` を配置してコンパイルしてください。

MT4でスクリプトを実行し、CSVからチャート用データを作成します。

## 注意

MT4のオフラインチャート/HST形式はビルドやブローカー環境によって挙動差があります。
本プロジェクトではまずCSV出力とMT4側読み込みを分離し、環境差に対応しやすい構成にしています。

## 納品範囲の想定

含む:

- J-Quants Standard API連携
- 日足OHLC取得
- 4661での検証
- CSV出力
- MT4 Filesフォルダへの配置
- MT4側CSV読み込みスクリプト
- 終値ライン表示インディケーター
- 手動更新bat
- 自動更新設定手順

含まない:

- Premiumデータ可視化
- 配当・売買内訳の描写
- 大量銘柄一括UI
- リアルタイム更新
- EA売買機能
