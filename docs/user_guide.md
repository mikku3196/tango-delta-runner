# Project Chimera ユーザーガイド

## はじめに

Project Chimeraは、新NISA（少額投資非課税制度）の非課税メリットを最大化し、ユーザーに代わって資産の購入、配当金の再投資、リバランスまでを全自動で行うシステムです。

## 前提条件

### 必要な環境
- **OS**: Ubuntu 22.04 LTS (CUI) または Windows 11 Home
- **Python**: 3.10以上
- **証券口座**: Interactive Brokers証券のNISA口座
- **Discord**: 通知用のDiscordサーバー

### 必要な知識
- 基本的なLinuxコマンド操作
- Pythonの基本的な理解
- 投資の基本的な知識

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/mikku3196/tango-delta-runner.git
cd tango-delta-runner
```

### 2. Python環境の準備

```bash
# Python仮想環境を作成
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt
```

### 3. Interactive Brokersの設定

1. **IB Client Portal Gatewayをダウンロード・インストール**
   - [Interactive Brokers公式サイト](https://www.interactivebrokers.com/en/trading/tws.php)からダウンロード

2. **Gatewayを起動**
   - ログイン後、API接続を有効化
   - ポート5000で接続を許可

3. **API設定の確認**
   - 設定 > API > 設定で以下を確認:
     - ソケットポート: 5000
     - マスターAPIクライアントID: 0
     - 読み取り専用API: 無効

### 4. Discord Webhookの設定

1. **DiscordサーバーでWebhookを作成**
   - サーバー設定 > 統合 > Webhook > 新しいWebhook
   - Webhook名: "Project Chimera"
   - チャンネル: 通知用チャンネルを選択

2. **Webhook URLをコピー**
   - 作成されたWebhookのURLをコピー

### 5. 設定ファイルの準備

```bash
# 環境変数ファイルを作成
cp .env.example .env

# .envファイルを編集
nano .env
```

`.env`ファイルの内容:
```env
# Interactive Brokers Account Credentials
IB_MAIN_ACCOUNT_ID="DU1234567"
IB_NISA_ACCOUNT_ID="FU7654321"

# Discord Notification Settings
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your_webhook_id/your_webhook_token"
```

### 6. 設定ファイルのカスタマイズ

`src/config/config.yaml`を編集して、投資戦略をカスタマイズ:

```yaml
# ポートフォリオ比率（リスク許容度に応じて調整）
portfolio_ratios:
  index: 0.50    # コア戦略（インデックス）
  dividend: 0.30 # サテライト①（高配当株）
  range: 0.20    # サテライト②（レンジ取引）

# 月次投資額
index_bot:
  monthly_investment: 30000  # 3万円

# 高配当株の保有数上限
dividend_bot:
  max_holding_stocks: 5
```

## 使用方法

### 1. システム起動

```bash
# メインシステムを起動
python src/main_controller.py
```

### 2. IB接続テスト

```bash
# IB接続をテスト
python test_ib_connection.py
```

### 3. 緊急停止

```bash
# 緊急停止を実行
python emergency_stop.py
```

### 4. バックテスト実行

```bash
# 5年間のバックテストを実行
python run_backtest.py --strategy all --years 5

# Discord通知付きで実行
python run_backtest.py --strategy portfolio --discord
```

### 5. バックテスト結果分析

```bash
# レポートを生成
python analyze_backtest.py --report backtest_report.md

# グラフを表示
python analyze_backtest.py --plot
```

## 投資戦略の説明

### コア戦略（インデックス投資）
- **目的**: 長期的な資産形成
- **対象**: 全世界株式インデックスファンド
- **口座**: NISAつみたて枠
- **頻度**: 毎月1日9:30に自動積立
- **特徴**: 安定した長期リターンを狙う

### サテライト①（高配当株投資）
- **目的**: 配当収入の獲得
- **対象**: 日本高配当株
- **口座**: NISA成長投資枠
- **頻度**: 毎週日曜22:00にスクリーニング、毎営業日9:05に購入判断
- **特徴**: 安定した配当収入を狙う

### サテライト②（レンジ取引）
- **目的**: 短期利益の獲得
- **対象**: レンジ相場の銘柄
- **口座**: 課税口座
- **頻度**: 取引時間中は常時監視
- **特徴**: ボリンジャーバンドを活用した短期売買

## リスク許容度の設定

### 安定型
- コア: 70%、サテライト①: 20%、サテライト②: 10%
- リスクを最小限に抑えた運用

### バランス型
- コア: 60%、サテライト①: 30%、サテライト②: 10%
- リスクとリターンのバランスを重視

### 積極型（デフォルト）
- コア: 50%、サテライト①: 30%、サテライト②: 20%
- 高いリターンを狙った積極的な運用

## 監視・通知

### Discord通知の種類

1. **取引実行通知**
   - 買い注文の実行
   - 売り注文の実行
   - 約定結果

2. **ポートフォリオリバランス通知**
   - リバランスの実行
   - 追加投資の実行

3. **NISA制限警告**
   - 年間枠の使用率が95%に達した場合
   - 生涯枠の使用率が95%に達した場合

4. **システムエラー通知**
   - Botの停止
   - API接続エラー
   - その他のシステムエラー

5. **定期レポート**
   - 日次サマリー
   - 週次レポート
   - 月次レポート

### ログファイルの確認

```bash
# 最新のログを確認
tail -f logs/chimera_$(date +%Y-%m-%d).log

# エラーログを検索
grep "ERROR" logs/chimera_*.log

# 取引ログを検索
grep "TRADE" logs/chimera_*.log
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. IB接続エラー
**症状**: "IB接続に失敗しました"というエラー

**解決方法**:
1. IB Client Portal Gatewayが起動しているか確認
2. API接続が有効になっているか確認
3. ポート5000で接続を許可しているか確認
4. ファイアウォールの設定を確認

#### 2. Discord通知エラー
**症状**: Discordに通知が送信されない

**解決方法**:
1. Webhook URLが正しいか確認
2. Discordサーバーの権限設定を確認
3. Webhookが削除されていないか確認

#### 3. Bot停止エラー
**症状**: Botが停止してしまう

**解決方法**:
1. Watchdogのログを確認
2. エラー数が上限を超えていないか確認
3. STOP.flagが存在していないか確認
4. システムリソースの使用状況を確認

#### 4. 取引エラー
**症状**: 注文が実行されない

**解決方法**:
1. 口座残高が十分か確認
2. 市場が開いているか確認
3. 銘柄コードが正しいか確認
4. 注文数量が適切か確認

### ログの確認方法

```bash
# システム全体のログ
tail -f logs/chimera_$(date +%Y-%m-%d).log

# 特定のBotのログ
grep "CORE_INDEX_BOT" logs/chimera_*.log
grep "SATELLITE_DIVIDEND_BOT" logs/chimera_*.log
grep "SATELLITE_RANGE_BOT" logs/chimera_*.log

# エラーログ
grep "ERROR" logs/chimera_*.log

# 取引ログ
grep "TRADE" logs/chimera_*.log
```

## セキュリティ

### 重要な注意事項

1. **機密情報の管理**
   - `.env`ファイルは絶対に公開しない
   - 口座IDやWebhook URLは他人に教えない

2. **自己責任**
   - 本システムは自己利用限定
   - 投資にはリスクが伴う
   - 最終責任はユーザーに帰属

3. **投資助言行為**
   - 本システムは投資助言行為を行わない
   - 投資判断は自己責任で行う

## メンテナンス

### 定期メンテナンス

1. **ログファイルの確認**
   - 週1回程度、ログファイルを確認
   - エラーがないかチェック

2. **システムリソースの確認**
   - CPU使用率
   - メモリ使用率
   - ディスク使用率

3. **設定の見直し**
   - 月1回程度、設定を見直し
   - 投資戦略の調整

### アップデート

```bash
# 最新版を取得
git pull origin main

# 依存関係を更新
pip install -r requirements.txt --upgrade
```

## サポート

### 問題報告

問題が発生した場合は、以下の情報を含めて報告してください:

1. エラーメッセージ
2. ログファイルの該当部分
3. 実行環境（OS、Pythonバージョン）
4. 再現手順

### よくある質問

**Q: システムは24時間稼働しますか？**
A: はい、システムは24時間稼働します。ただし、取引は市場の営業時間内のみ実行されます。

**Q: 手動で取引を実行できますか？**
A: はい、緊急停止機能を使用してシステムを停止し、手動で取引を実行できます。

**Q: 投資戦略を変更できますか？**
A: はい、`config.yaml`ファイルを編集して投資戦略を変更できます。

**Q: バックテストはどのくらいの期間で実行できますか？**
A: 最大5年間のバックテストを実行できます。ただし、データの可用性に依存します。

## 免責事項

- 本システムは個人利用を目的としており、商用利用は禁止されています
- 投資にはリスクが伴います
- 過去の実績は将来の運用成果を保証するものではありません
- システムの動作は事前に十分テストしてください
- 最終責任はユーザーに帰属します
