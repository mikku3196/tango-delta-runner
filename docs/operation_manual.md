# Project Chimera 運用マニュアル

## 概要

Project Chimeraは、新NISA（少額投資非課税制度）の非課税メリットを最大化し、ユーザーに代わって資産の購入、配当金の再投資、リバランスまでを全自動で行うシステムです。

## 運用開始前の準備

### 1. システム要件の確認

#### 必要な環境
- **OS**: Ubuntu 22.04 LTS (CUI) または Windows 11 Home
- **Python**: 3.10以上
- **メモリ**: 4GB以上
- **ディスク**: 10GB以上の空き容量
- **ネットワーク**: 安定したインターネット接続

#### 必要なアカウント
- **Interactive Brokers証券**: NISA口座
- **Discord**: 通知用のDiscordサーバー

### 2. 初期セットアップ

#### リポジトリのクローン
```bash
git clone https://github.com/mikku3196/tango-delta-runner.git
cd tango-delta-runner
```

#### Python環境の準備
```bash
# Python仮想環境を作成
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt
```

#### 設定ファイルの準備
```bash
# 環境変数ファイルを作成
cp .env.example .env

# .envファイルを編集
nano .env
```

#### 設定ファイルのカスタマイズ
```bash
# 設定最適化スクリプトを実行
python scripts/optimize_config.py
```

### 3. 事前テスト

#### 本番環境テスト
```bash
python scripts/production_test.py
```

#### 実際のテスト実行
```bash
python scripts/run_actual_tests.py
```

## 日常運用

### 1. システム起動

#### 手動起動
```bash
python src/main_controller.py
```

#### サービスとして起動（Ubuntu）
```bash
# systemdサービスファイルをインストール
sudo cp chimera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable chimera
sudo systemctl start chimera

# サービス状態を確認
sudo systemctl status chimera
```

### 2. 監視

#### 監視ダッシュボード
```bash
# ダッシュボードを起動
python start_dashboard.py

# ブラウザでアクセス
# http://localhost:5001
```

#### ログ監視
```bash
# 最新のログを確認
tail -f logs/chimera_$(date +%Y-%m-%d).log

# エラーログを検索
grep "ERROR" logs/chimera_*.log

# 取引ログを検索
grep "TRADE" logs/chimera_*.log
```

#### Discord通知
- 取引実行通知
- ポートフォリオリバランス通知
- NISA制限警告
- システムエラー通知
- 定期レポート

### 3. 定期メンテナンス

#### 日次チェック
- [ ] システムが正常に動作しているか
- [ ] Discord通知が正常に送信されているか
- [ ] ログファイルにエラーがないか
- [ ] NISA非課税枠の使用状況

#### 週次チェック
- [ ] ポートフォリオの状態
- [ ] バックテスト結果の確認
- [ ] システムリソースの使用状況
- [ ] セキュリティ監査の実行

#### 月次チェック
- [ ] パフォーマンスレビュー
- [ ] 設定の見直し
- [ ] バックアップの確認
- [ ] システムアップデートの確認

## 投資戦略の管理

### 1. コア戦略（インデックス投資）

#### 設定
- **対象**: 全世界株式インデックスファンド
- **口座**: NISAつみたて枠
- **頻度**: 毎月1日9:30
- **金額**: 設定ファイルで指定

#### 監視ポイント
- 月次積立の実行状況
- インデックスファンドのパフォーマンス
- NISAつみたて枠の使用状況

### 2. サテライト①（高配当株投資）

#### 設定
- **対象**: 日本高配当株
- **口座**: NISA成長投資枠
- **頻度**: 毎週日曜22:00にスクリーニング、毎営業日9:05に購入判断
- **最大保有数**: 設定ファイルで指定

#### 監視ポイント
- スクリーニング結果
- 購入・売却の実行状況
- 配当金の受取状況
- 保有銘柄のパフォーマンス

### 3. サテライト②（レンジ取引）

#### 設定
- **対象**: レンジ相場の銘柄
- **口座**: 課税口座
- **頻度**: 取引時間中は常時監視
- **手法**: ボリンジャーバンドを活用

#### 監視ポイント
- 取引シグナルの発生
- 売買の実行状況
- 損益の状況
- ポジションの管理

## リスク管理

### 1. NISA非課税枠の管理

#### 年間枠（360万円）
- 使用率95%でアラート
- 上限到達時は自動停止
- 売却により復活した枠は翌年計画に反映

#### 生涯枠（1,800万円）
- 使用率95%でアラート
- 上限到達時は自動停止
- 長期計画の見直し

### 2. ポートフォリオリバランス

#### 自動リバランス
- 比率乖離時は入金によるリバランスを優先
- NISA内では安易な売却を行わない
- リバランス実行時にDiscord通知

#### 手動リバランス
- 緊急時は手動でリバランスを実行
- 設定ファイルの比率を調整
- システム再起動で反映

### 3. 緊急停止

#### 緊急停止の実行
```bash
python emergency_stop.py
```

#### 緊急停止の解除
```bash
python emergency_stop.py
# STOP.flagの削除を選択
```

## トラブルシューティング

### 1. よくある問題

#### IB接続エラー
**症状**: "IB接続に失敗しました"というエラー

**解決方法**:
1. IB Client Portal Gatewayが起動しているか確認
2. API接続が有効になっているか確認
3. ポート5000で接続を許可しているか確認
4. ファイアウォールの設定を確認

#### Discord通知エラー
**症状**: Discordに通知が送信されない

**解決方法**:
1. Webhook URLが正しいか確認
2. Discordサーバーの権限設定を確認
3. Webhookが削除されていないか確認

#### Bot停止エラー
**症状**: Botが停止してしまう

**解決方法**:
1. Watchdogのログを確認
2. エラー数が上限を超えていないか確認
3. STOP.flagが存在していないか確認
4. システムリソースの使用状況を確認

### 2. ログの確認方法

#### システム全体のログ
```bash
tail -f logs/chimera_$(date +%Y-%m-%d).log
```

#### 特定のBotのログ
```bash
grep "CORE_INDEX_BOT" logs/chimera_*.log
grep "SATELLITE_DIVIDEND_BOT" logs/chimera_*.log
grep "SATELLITE_RANGE_BOT" logs/chimera_*.log
```

#### エラーログ
```bash
grep "ERROR" logs/chimera_*.log
```

#### 取引ログ
```bash
grep "TRADE" logs/chimera_*.log
```

### 3. システム復旧

#### サービス再起動
```bash
# systemdサービスの場合
sudo systemctl restart chimera

# 手動起動の場合
# Ctrl+Cで停止後、再起動
python src/main_controller.py
```

#### 設定のリセット
```bash
# 設定ファイルをバックアップ
cp src/config/config.yaml src/config/config.yaml.backup

# デフォルト設定に戻す
git checkout src/config/config.yaml
```

## パフォーマンス監視

### 1. システムリソース

#### CPU使用率
- 80%以上で警告
- 90%以上で緊急停止

#### メモリ使用率
- 80%以上で警告
- 90%以上で緊急停止

#### ディスク使用率
- 90%以上で警告
- 95%以上で緊急停止

### 2. パフォーマンス最適化

#### 自動最適化
```bash
python scripts/performance_optimizer.py
```

#### 手動最適化
- 古いログファイルの削除
- 不要なプロセスの終了
- メモリのクリーンアップ
- 一時ファイルの削除

## セキュリティ管理

### 1. セキュリティ監査

#### 定期監査
```bash
python scripts/security_enhancer.py
```

#### 監査項目
- ファイル権限
- 機密ファイルの保護
- パスワードセキュリティ
- APIセキュリティ
- ログセキュリティ
- ネットワークセキュリティ

### 2. セキュリティ強化

#### 自動強化
- ファイル権限の修正
- 機密ファイルの保護
- ログセキュリティの強化
- 設定ファイルの強化

#### 手動強化
- 定期的なパスワード変更
- アクセス権限の最小化
- セキュリティアップデートの適用
- バックアップの暗号化

## バックアップと復旧

### 1. バックアップ

#### 自動バックアップ
```bash
# バックアップスクリプトを設定
crontab -e
# 毎日深夜2時にバックアップ実行
0 2 * * * /path/to/backup_chimera.sh
```

#### 手動バックアップ
```bash
# 設定ファイルのバックアップ
cp src/config/config.yaml src/config/config.yaml.backup
cp .env .env.backup

# ログファイルのバックアップ
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

### 2. 復旧

#### 設定ファイルの復旧
```bash
cp src/config/config.yaml.backup src/config/config.yaml
cp .env.backup .env
```

#### ログファイルの復旧
```bash
tar -xzf logs_backup_YYYYMMDD.tar.gz
```

## アップデート

### 1. システムアップデート

#### 自動アップデート
```bash
python scripts/deployment.py
```

#### 手動アップデート
```bash
# 最新版を取得
git pull origin main

# 依存関係を更新
pip install -r requirements.txt --upgrade

# システムを再起動
sudo systemctl restart chimera
```

### 2. 設定の移行

#### 設定ファイルの移行
```bash
# 現在の設定をバックアップ
cp src/config/config.yaml src/config/config.yaml.backup

# 新しい設定ファイルを確認
git diff src/config/config.yaml

# 必要に応じて手動で調整
nano src/config/config.yaml
```

## 運用レポート

### 1. 日次レポート

#### 自動生成
- システムが自動的に生成
- Discordに送信
- ログファイルに保存

#### 内容
- 取引実行状況
- ポートフォリオの状態
- NISA非課税枠の使用状況
- システムエラーの有無

### 2. 週次レポート

#### 自動生成
- 毎週日曜日に生成
- Discordに送信
- ログファイルに保存

#### 内容
- 週間パフォーマンス
- ポートフォリオの変化
- リスク指標
- 推奨事項

### 3. 月次レポート

#### 自動生成
- 毎月1日に生成
- Discordに送信
- ログファイルに保存

#### 内容
- 月間パフォーマンス
- 年間累積パフォーマンス
- リバランスの実行状況
- 今後の方針

## 連絡先とサポート

### 1. 緊急時連絡先

#### システム停止時
- Discord通知を確認
- ログファイルを確認
- 緊急停止スクリプトを実行

#### 取引エラー時
- IB証券のサポートに連絡
- 手動で注文を確認
- システムを再起動

### 2. サポート情報

#### ログファイル
- `logs/chimera_YYYY-MM-DD.log`
- `logs/backtest_results/`
- `operation_log.json`

#### 設定ファイル
- `src/config/config.yaml`
- `.env`
- `config_optimization_report.json`

#### テスト結果
- `test_execution_report.json`
- `production_test_report.json`
- `security_audit_result.json`

## 免責事項

- 本システムは個人利用を目的としており、商用利用は禁止されています
- 投資にはリスクが伴います
- 過去の実績は将来の運用成果を保証するものではありません
- システムの動作は事前に十分テストしてください
- 最終責任はユーザーに帰属します
- 投資助言行為を行わない明示
- 法令遵守と自己責任の原則
