# セットアップ手順

## 1. クライアントへ確認すること

- J-Quants APIキーは再発行済みか
- J-Quants Standardプランが利用可能か
- 検証銘柄は 4661 で問題ないか
- MT4のデータフォルダパス
- XMTrading MT4のサーバー名
- 毎日AM7:00更新で問題ないか

## 2. MT4データフォルダ確認

MT4を開き、以下を確認します。

`ファイル > データフォルダを開く`

表示されたパスを `config/config.json` の `terminal_data_path` に設定します。

例:

```json
"terminal_data_path": "C:/Users/User/AppData/Roaming/MetaQuotes/Terminal/ABCDEF123456"
```

## 3. Python設定

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy config\config.example.json config\config.json
```

`config/config.json` にAPIキーを設定します。

## 4. 取得・変換テスト

```bat
python scripts\update_stock_data.py --config config\config.json
```

成功すると以下ができます。

```text
data/raw/4661_daily_quotes_raw.csv
data/processed/JP4661_D1_ohlc.csv
data/mt4_csv/JP4661_D1.csv
```

## 5. MT4へCSVコピー

```bat
python scripts\install_to_mt4.py --config config\config.json
```

コピー先:

```text
<Mt4DataFolder>/MQL4/Files/JP4661_D1.csv
```

## 6. MQL4ファイル配置

以下をMT4データフォルダへコピーします。

```text
mt4/MQL4/Scripts/JPStock_ImportCsv_OfflineChart.mq4
mt4/MQL4/Indicators/JPStock_CloseLine_FromCsv.mq4
```

コピー先:

```text
<Mt4DataFolder>/MQL4/Scripts/
<Mt4DataFolder>/MQL4/Indicators/
```

MetaEditorでコンパイルします。

## 7. オフラインチャート生成

MT4で任意チャートを開き、`JPStock_ImportCsv_OfflineChart` スクリプトを実行します。

その後:

`ファイル > オフラインチャート`

から `JP4661,D1` または近い名称を探して開きます。

## 8. 既存インディケーター確認

オフラインチャート上に以下を適用して確認します。

- Moving Average
- Bollinger Bands
- RSI

## 9. AM7:00自動更新

PowerShellを管理者権限で開きます。

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\create_windows_task.ps1
```

作成後、タスクスケジューラで `JQuants_MT4_Stock_Update_0700` を確認します。

## 10. 注意

MT4で開いているオフラインチャートが自動で再描画されない場合があります。
その場合は、チャートの再オープン、または更新用MQL4処理の追加が必要です。

初回納品では、まず「取得・変換・表示・インディケーター利用確認」を優先してください。
