# Project Chimera - NISA口座最適活用・全自動資産運用プログラム

## 概要
Project Chimeraは、新NISA（少額投資非課税制度）の非課税メリットを最大化し、ユーザーに代わって資産の購入、配当金の再投資、リバランスまでを全自動で行うシステムです。

## 主要機能

### 1. コア・サテライト運用戦略
- **コア戦略**: NISAつみたて枠で全世界株式インデックスファンドを積立投資
- **サテライト①**: 成長投資枠で日本高配当株を自動選定・購入
- **サテライト②**: 課税口座でボリンジャーバンドを活用した短期売買

### 2. 自動投資・運用機能
- 月次積立投資の自動実行
- 高配当株のスクリーニングと自動購入
- レンジ相場での短期売買
- ポートフォリオの自動リバランス

### 3. NISA非課税枠の最適管理
- 年間枠360万円、生涯枠1,800万円の常時監視
- 上限到達時の自動停止とDiscord通知
- 売却による枠復活の翌年計画への反映

### 4. 緊急停止機能 (Manual Override)
- `emergency_stop.py`による全注文キャンセル
- STOP.flagによるシステム停止
- DiscordへのCRITICAL通知

### 5. リスク許容度診断
- 「安定」「バランス」「積極」の3段階診断
- 診断結果に応じたポートフォリオ比率の自動設定

### 6. 詳細ロギング
- JSONL形式での詳細ログ記録
- 7日間または50MB超でのローテーション

## 技術仕様

### 実行環境
- **OS**: Ubuntu 22.04 LTS (CUI)
- **言語**: Python 3.10+
- **取引API**: Interactive Brokers
- **通知**: Discord Webhook

### 主要ライブラリ
- `ibapi`: Interactive Brokers API
- `pandas`: データ分析
- `numpy`: 数値計算
- `requests`: HTTP通信
- `apscheduler`: スケジューリング
- `yfinance`: 株価データ取得
- `beautifulsoup4`: Webスクレイピング

## ファイル構成

```
tango-delta-runner/
├── src/
│   ├── main_controller.py          # メインコントローラー
│   ├── config/
│   │   └── config.yaml            # 公開設定ファイル
│   ├── shared_modules/
│   │   ├── config_loader.py       # 設定読み込み
│   │   ├── discord_logger.py      # Discord通知
│   │   ├── ib_connector.py        # IB API接続
│   │   ├── nisa_monitor.py        # NISA監視
│   │   └── risk_assessor.py       # リスク診断
│   └── bots/
│       ├── core_index_bot.py      # コア戦略Bot
│       ├── satellite_dividend_bot.py # 高配当株Bot
│       └── satellite_range_bot.py # レンジ取引Bot
├── emergency_stop.py              # 緊急停止スクリプト
├── test_ib_connection.py         # IB接続テスト
├── .env.example                   # 環境変数テンプレート
├── requirements.txt               # 依存関係
└── README.md                      # このファイル
```

## セットアップ

### 1. 環境準備
```bash
# リポジトリをクローン
git clone https://github.com/mikku3196/tango-delta-runner.git
cd tango-delta-runner

# Python仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. 設定ファイルの準備
```bash
# 環境変数ファイルを作成
cp .env.example .env
# .envファイルを編集して機密情報を設定

# 設定ファイルを編集
nano src/config/config.yaml
```

### 3. IB Gatewayの設定
1. Interactive Brokers Client Portal Gatewayを起動
2. API接続を有効化
3. ポート5000で接続を許可

### 4. Discord Webhookの設定
1. DiscordサーバーでWebhookを作成
2. Webhook URLを`.env`ファイルに設定

## 使用方法

### システム起動
```bash
python src/main_controller.py
```

### IB接続テスト
```bash
python test_ib_connection.py
```

### 緊急停止
```bash
python emergency_stop.py
```

## スケジュール

- **インデックス積立**: 毎月1日 9:30
- **高配当株スクリーニング**: 毎週日曜 22:00
- **高配当株購入判断**: 毎営業日 9:05
- **レンジ相場スクリーニング**: 毎営業日 16:00
- **レンジ取引**: 取引時間中 常時実行
- **ポートフォリオリバランス**: 毎月1日 10:00
- **NISA使用状況レポート**: 毎日 18:00

## セキュリティ

- 機密情報は`.env`ファイルに分離
- 公開設定値のみ`config.yaml`に保持
- 自己利用限定（投資助言行為を行わない）

## 注意事項

- 本システムは自己責任でご利用ください
- 投資にはリスクが伴います
- 過去の実績は将来の運用成果を保証するものではありません
- システムの動作は事前に十分テストしてください

## ライセンス

このプロジェクトは個人利用を目的としており、商用利用は禁止されています。

## サポート

問題が発生した場合は、Discord通知またはログファイルを確認してください。