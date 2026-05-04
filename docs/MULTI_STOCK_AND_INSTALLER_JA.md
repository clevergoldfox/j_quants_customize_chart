# 複数銘柄更新・ワンクリックインストーラー手順

## 1. 追加されるもの

このパッチで以下を追加します。

```text
config/config.multistock.example.json
scripts/update_multi_stocks.py
scripts/update_multi_stocks.bat
scripts/one_click_install.bat
scripts/create_windows_task_bat.bat
```

## 2. 複数銘柄設定

`config/config.json` に以下のように `stocks` を追加します。

```json
"stocks": [
  {"code": "46610", "symbol": "JP4661", "name": "Oriental Land"},
  {"code": "72030", "symbol": "JP7203", "name": "Toyota"},
  {"code": "67580", "symbol": "JP6758", "name": "Sony Group"}
]
```

J-Quants V2では、通常4桁コードの末尾に `0` を付けた5桁コードを使用します。

例:

```text
4661 -> 46610
7203 -> 72030
6758 -> 67580
```

## 3. 複数銘柄更新

以下を実行します。

```bat
scripts\update_multi_stocks.bat
```

または直接:

```bat
python scripts\update_multi_stocks.py --config config\config.json --install
```

生成されるCSV例:

```text
data/mt4_csv/JP4661_D1.csv
data/mt4_csv/JP7203_D1.csv
data/mt4_csv/JP6758_D1.csv
```

MT4の `MQL4/Files` にもコピーされます。

## 4. MT4側で複数銘柄を表示

MT4で `JPStock_ImportCsv_OfflineChart` を実行するときに、入力値を変えます。

4661:

```text
InpCsvFile = JP4661_D1.csv
InpOfflineSymbol = JP4661
```

7203:

```text
InpCsvFile = JP7203_D1.csv
InpOfflineSymbol = JP7203
```

6758:

```text
InpCsvFile = JP6758_D1.csv
InpOfflineSymbol = JP6758
```

その後:

```text
File > Open Offline
```

から各銘柄のD1チャートを開きます。

## 5. ワンクリックインストーラー

以下を実行します。

```bat
scripts\one_click_install.bat
```

実行内容:

- Python仮想環境作成
- requirements.txt インストール
- config/config.json 作成
- MT4データフォルダが設定済みならMQ4ファイルをコピー
- AM7:00のWindowsタスク作成

## 6. PowerShellを使わない自動更新タスク作成

PowerShell実行ポリシー問題を避ける場合:

```bat
scripts\create_windows_task_bat.bat
```

を管理者として実行してください。

## 7. クライアント向け説明

今回の拡張により、初期の4661だけでなく、設定ファイルに銘柄を追加することで複数銘柄のデータを一括取得・変換できる構成にしています。

また、初期設定・依存関係インストール・自動更新タスク作成をまとめて行うワンクリックインストーラーを用意しているため、導入時の手間を抑えられます。
