# Project Chimera 技術仕様書

## 概要

Project Chimeraは、新NISA（少額投資非課税制度）の非課税メリットを最大化し、ユーザーに代わって資産の購入、配当金の再投資、リバランスまでを全自動で行うシステムです。

## アーキテクチャ

### システム構成

```
Project Chimera
├── メインコントローラー (main_controller.py)
├── Bot群
│   ├── コア戦略Bot (core_index_bot.py)
│   ├── 高配当株Bot (satellite_dividend_bot.py)
│   └── レンジ取引Bot (satellite_range_bot.py)
├── 共有モジュール
│   ├── 設定ローダー (config_loader.py)
│   ├── Discord通知 (discord_logger.py)
│   ├── IB接続 (ib_connector.py)
│   ├── NISA監視 (nisa_monitor.py)
│   ├── リスク診断 (risk_assessor.py)
│   ├── 詳細ログ (detailed_logger.py)
│   └── Watchdog (watchdog.py)
├── バックテスト
│   └── バックテストエンジン (backtest_engine.py)
└── 設定ファイル
    ├── config.yaml
    └── .env
```

### データフロー

1. **設定読み込み**: `config.yaml`と`.env`から設定を読み込み
2. **Bot初期化**: 各Botを初期化し、Watchdogに登録
3. **スケジューラー設定**: APSchedulerで定期実行タスクを設定
4. **監視開始**: Watchdogが各Botのヘルスチェックを開始
5. **取引実行**: 各Botがスケジュールに従って取引を実行
6. **ログ記録**: 詳細ログとDiscord通知で結果を記録

## 主要機能

### 1. コア戦略Bot

**目的**: NISAつみたて枠で全世界株式インデックスファンドを積立投資

**機能**:
- 毎月1日9:30に自動積立実行
- リバランス時の追加投資
- ヘルスチェック機能

**実装詳細**:
```python
class CoreIndexBot:
    def execute_monthly_investment(self):
        # 月次積立投資の実行
        # IB APIを使用して成行買い注文
        # 詳細ログとDiscord通知
    
    def is_healthy(self) -> bool:
        # Botのヘルスチェック
        # エラー数、実行時間、状態を確認
```

### 2. 高配当株Bot

**目的**: NISA成長投資枠で日本高配当株を自動選定・購入

**機能**:
- 毎週日曜22:00にスクリーニング実行
- 毎営業日9:05に購入判断
- 最大5銘柄まで保有

**スクリーニング基準**:
- 配当利回り: 4.0%以上
- 自己資本比率: 50%以上
- PER: 25倍以下
- 配当カットなし年数: 10年以上

### 3. レンジ取引Bot

**目的**: 課税口座でボリンジャーバンドを活用した短期売買

**機能**:
- 毎営業日16:00にスクリーニング
- 取引時間中は常時監視
- ボリンジャーバンドのブレイクアウトで売買

**取引ルール**:
- ボリンジャーバンド期間: 20日
- 標準偏差: 2.0
- ストップロス: 2%

### 4. NISA監視機能

**目的**: NISA非課税枠の最適管理

**機能**:
- 年間枠360万円、生涯枠1,800万円の監視
- 95%使用時にアラート
- 毎日18:00に使用状況レポート

### 5. 緊急停止機能

**目的**: 手動介入によるシステム停止

**機能**:
- `emergency_stop.py`による全注文キャンセル
- STOP.flagによるシステム停止
- DiscordへのCRITICAL通知

### 6. Watchdog機能

**目的**: システム監視と自動再起動

**機能**:
- 10分ごとの生存確認
- 最大3回の再起動試行
- 5分間のクールダウン期間
- 24時間ごとのハートビート通知

### 7. 詳細ログ機能

**目的**: システムの詳細な動作記録

**機能**:
- JSONL形式でのログ記録
- 7日間または50MB超でローテーション
- 取引、ポートフォリオ、NISA使用状況の詳細記録

### 8. バックテスト機能

**目的**: 過去データでの戦略検証

**機能**:
- `yfinance`を使用したデータ取得
- 各戦略の個別バックテスト
- ポートフォリオ全体のバックテスト
- 結果の可視化と分析

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
- `matplotlib`: グラフ作成
- `seaborn`: 統計的可視化

### 設定ファイル

#### config.yaml
公開設定値を格納:
- IB Gateway設定
- ポートフォリオ比率
- Bot設定
- NISA設定
- ログ設定
- Watchdog設定

#### .env
機密情報を格納:
- IB口座ID
- Discord Webhook URL

### セキュリティ

- 機密情報は`.env`ファイルに分離
- 公開設定値のみ`config.yaml`に保持
- 自己利用限定（投資助言行為を行わない）

## 運用監視

### ログ管理
- 詳細ログ: `logs/chimera_YYYY-MM-DD.log`
- バックテスト結果: `logs/backtest_results/`
- ログローテーション: 7日間または50MB超

### 通知設定
- 取引実行: ✅
- ポートフォリオリバランス: ✅
- NISA制限警告: ✅
- システムエラー: ✅
- 日次サマリー: ✅
- 週次レポート: ✅
- 月次レポート: ✅

### パフォーマンス監視
- CPU使用率上限: 80%
- メモリ使用率上限: 80%
- ディスク使用率上限: 90%

## トラブルシューティング

### よくある問題

1. **IB接続エラー**
   - IB Client Portal Gatewayが起動しているか確認
   - API接続が有効になっているか確認
   - ポート5000で接続を許可しているか確認

2. **Discord通知エラー**
   - Webhook URLが正しいか確認
   - Discordサーバーの権限設定を確認

3. **Bot停止エラー**
   - Watchdogのログを確認
   - エラー数が上限を超えていないか確認
   - STOP.flagが存在していないか確認

### ログ確認方法

```bash
# 最新のログを確認
tail -f logs/chimera_$(date +%Y-%m-%d).log

# エラーログを検索
grep "ERROR" logs/chimera_*.log

# 取引ログを検索
grep "TRADE" logs/chimera_*.log
```

## 開発・テスト

### テスト実行

```bash
# 全テスト実行
python run_tests.py --all

# 単体テストのみ
python run_tests.py --unit

# バックテストテスト
python run_tests.py --backtest
```

### バックテスト実行

```bash
# 全戦略のバックテスト
python run_backtest.py --strategy all --years 5

# インデックス戦略のみ
python run_backtest.py --strategy index --years 3

# Discord通知付き
python run_backtest.py --strategy portfolio --discord
```

### バックテスト結果分析

```bash
# レポート生成
python analyze_backtest.py --report backtest_report.md

# グラフ表示
python analyze_backtest.py --plot

# ポートフォリオ進化をプロット
python analyze_backtest.py --portfolio-evolution index
```

## 今後の拡張予定

### v4.0系で検討
- パフォーマンス計測機能
- バックテスト結果の自動保存
- ハートビート監視の二重化
- より高度なリスク管理
- 機械学習による予測機能

## ライセンス

このプロジェクトは個人利用を目的としており、商用利用は禁止されています。

## サポート

問題が発生した場合は、Discord通知またはログファイルを確認してください。
