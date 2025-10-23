# Project Chimera トラブルシューティングガイド

## 概要

このガイドは、Project Chimeraの運用中に発生する可能性のある問題とその解決方法をまとめたものです。

## 問題の分類

### 1. 緊急度による分類

#### 🔴 緊急（Critical）
- システムが完全に停止している
- 取引が実行されない
- データが失われている
- セキュリティ侵害が疑われる

#### 🟡 重要（High）
- 一部の機能が動作しない
- パフォーマンスが大幅に低下している
- 通知が送信されない
- ログにエラーが記録されている

#### 🟢 軽微（Medium）
- 設定の問題
- 軽微なエラー
- パフォーマンスの軽微な低下
- 警告メッセージの表示

### 2. カテゴリによる分類

#### システム関連
- 起動・停止の問題
- パフォーマンスの問題
- リソース不足
- 依存関係の問題

#### 取引関連
- IB接続の問題
- 注文実行の問題
- データ取得の問題
- 約定の問題

#### 通知関連
- Discord通知の問題
- ログ出力の問題
- レポート生成の問題

#### 設定関連
- 設定ファイルの問題
- 環境変数の問題
- 権限の問題

## 緊急時の対応手順

### 1. システム完全停止時

#### 症状
- システムが応答しない
- プロセスが存在しない
- ログが更新されない

#### 対応手順
1. **緊急停止の実行**
   ```bash
   python emergency_stop.py
   ```

2. **プロセスの確認**
   ```bash
   ps aux | grep python
   ps aux | grep main_controller
   ```

3. **ログの確認**
   ```bash
   tail -f logs/chimera_$(date +%Y-%m-%d).log
   ```

4. **システムリソースの確認**
   ```bash
   top
   df -h
   free -h
   ```

5. **サービス再起動**
   ```bash
   sudo systemctl restart chimera
   ```

### 2. 取引が実行されない時

#### 症状
- 注文が発注されない
- 約定が発生しない
- IB接続エラーが発生

#### 対応手順
1. **IB接続の確認**
   ```bash
   python test_ib_connection.py
   ```

2. **IB Client Portal Gatewayの確認**
   - Gatewayが起動しているか
   - API接続が有効になっているか
   - ポート5000で接続を許可しているか

3. **口座残高の確認**
   - 十分な残高があるか
   - 取引可能な状態か

4. **市場時間の確認**
   - 取引時間内か
   - 祝日・休日でないか

### 3. 通知が送信されない時

#### 症状
- Discord通知が届かない
- ログに通知エラーが記録される
- Webhook URLエラーが発生

#### 対応手順
1. **Webhook URLの確認**
   ```bash
   grep "discord_webhook_url" .env
   ```

2. **Discord設定の確認**
   - Webhookが削除されていないか
   - サーバーの権限設定は適切か
   - チャンネルが存在するか

3. **ネットワーク接続の確認**
   ```bash
   ping discord.com
   curl -I https://discord.com/api/webhooks/
   ```

4. **通知設定の確認**
   ```bash
   grep "notifications" src/config/config.yaml
   ```

## 具体的な問題と解決方法

### 1. システム起動の問題

#### 問題: システムが起動しない

**症状**:
```
ModuleNotFoundError: No module named 'src'
ImportError: cannot import name 'ConfigLoader'
```

**原因**:
- Pythonパスが正しく設定されていない
- 依存関係がインストールされていない
- 仮想環境がアクティブでない

**解決方法**:
```bash
# 仮想環境をアクティブ化
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# Pythonパスを設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# システムを起動
python src/main_controller.py
```

#### 問題: 設定ファイルが見つからない

**症状**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'src/config/config.yaml'
```

**原因**:
- 設定ファイルが存在しない
- ファイルパスが間違っている
- 権限が不足している

**解決方法**:
```bash
# 設定ファイルの存在確認
ls -la src/config/

# 設定ファイルの権限確認
ls -la src/config/config.yaml

# 権限を修正
chmod 644 src/config/config.yaml
```

### 2. IB接続の問題

#### 問題: IB Gatewayに接続できない

**症状**:
```
ConnectionError: Failed to connect to IB Gateway
TimeoutError: Connection timeout
```

**原因**:
- IB Client Portal Gatewayが起動していない
- API接続が無効
- ファイアウォールの設定
- ポート番号が間違っている

**解決方法**:
1. **IB Client Portal Gatewayの起動**
   - Gatewayを起動
   - ログイン
   - API接続を有効化

2. **API設定の確認**
   - 設定 > API > 設定
   - ソケットポート: 5000
   - マスターAPIクライアントID: 0
   - 読み取り専用API: 無効

3. **ファイアウォールの設定**
   ```bash
   # Ubuntuの場合
   sudo ufw allow 5000
   
   # Windowsの場合
   # Windows Defender ファイアウォールでポート5000を許可
   ```

4. **接続テスト**
   ```bash
   python test_ib_connection.py
   ```

#### 問題: 認証エラー

**症状**:
```
AuthenticationError: Invalid credentials
PermissionError: Access denied
```

**原因**:
- 口座IDが間違っている
- パスワードが間違っている
- 2要素認証が有効
- 口座が凍結されている

**解決方法**:
1. **口座情報の確認**
   ```bash
   grep "IB_" .env
   ```

2. **2要素認証の確認**
   - Gatewayで2要素認証を無効化
   - または認証コードを入力

3. **口座状態の確認**
   - IB証券のウェブサイトで口座状態を確認
   - 必要に応じてサポートに連絡

### 3. 取引実行の問題

#### 問題: 注文が発注されない

**症状**:
```
OrderError: Order rejected
ValidationError: Invalid order parameters
```

**原因**:
- 注文パラメータが無効
- 口座残高が不足
- 市場が閉まっている
- 銘柄コードが間違っている

**解決方法**:
1. **注文パラメータの確認**
   ```bash
   grep "ticker" src/config/config.yaml
   grep "monthly_investment" src/config/config.yaml
   ```

2. **口座残高の確認**
   - IB証券のウェブサイトで残高を確認
   - 取引可能な残高を確認

3. **市場時間の確認**
   - 取引時間内か確認
   - 祝日・休日でないか確認

4. **銘柄コードの確認**
   - 正しい銘柄コードか確認
   - 取引可能な銘柄か確認

#### 問題: 約定が発生しない

**症状**:
- 注文は発注されたが約定しない
- 部分約定のみ
- 約定キャンセル

**原因**:
- 価格が適正でない
- 流動性が不足
- 市場の変動が激しい
- 注文タイプが適切でない

**解決方法**:
1. **注文タイプの確認**
   - 成行注文 vs 指値注文
   - 適切な注文タイプを選択

2. **価格の確認**
   - 現在価格を確認
   - 適正な価格で発注

3. **流動性の確認**
   - 出来高を確認
   - スプレッドを確認

### 4. 通知の問題

#### 問題: Discord通知が届かない

**症状**:
```
DiscordError: Webhook URL invalid
HTTPError: 404 Not Found
```

**原因**:
- Webhook URLが間違っている
- Webhookが削除されている
- Discordサーバーの権限が不足
- ネットワーク接続の問題

**解決方法**:
1. **Webhook URLの確認**
   ```bash
   grep "DISCORD_WEBHOOK_URL" .env
   ```

2. **Webhookの再作成**
   - DiscordサーバーでWebhookを再作成
   - 新しいURLを.envファイルに設定

3. **権限の確認**
   - Webhookの権限を確認
   - チャンネルの権限を確認

4. **接続テスト**
   ```bash
   curl -X POST -H "Content-Type: application/json" \
        -d '{"content":"Test message"}' \
        YOUR_WEBHOOK_URL
   ```

#### 問題: ログが出力されない

**症状**:
- ログファイルが作成されない
- ログが更新されない
- ログレベルが適切でない

**原因**:
- ログディレクトリの権限
- ログレベルの設定
- ディスク容量不足
- ログローテーションの問題

**解決方法**:
1. **ログディレクトリの確認**
   ```bash
   ls -la logs/
   chmod 755 logs/
   ```

2. **ログレベルの確認**
   ```bash
   grep "level" src/config/config.yaml
   ```

3. **ディスク容量の確認**
   ```bash
   df -h
   ```

4. **ログローテーションの設定**
   ```bash
   sudo cp chimera.logrotate /etc/logrotate.d/chimera
   ```

### 5. パフォーマンスの問題

#### 問題: システムが重い

**症状**:
- CPU使用率が高い
- メモリ使用率が高い
- 応答が遅い
- タイムアウトが発生

**原因**:
- リソース不足
- メモリリーク
- 無限ループ
- 外部APIの応答遅延

**解決方法**:
1. **リソース使用状況の確認**
   ```bash
   top
   htop
   free -h
   ```

2. **プロセスの確認**
   ```bash
   ps aux | grep python
   ```

3. **パフォーマンス最適化**
   ```bash
   python scripts/performance_optimizer.py
   ```

4. **システム再起動**
   ```bash
   sudo systemctl restart chimera
   ```

#### 問題: メモリ不足

**症状**:
```
MemoryError: Unable to allocate memory
OutOfMemoryError: Java heap space
```

**原因**:
- メモリリーク
- 大量のデータ処理
- システムメモリ不足
- 仮想メモリの設定

**解決方法**:
1. **メモリ使用状況の確認**
   ```bash
   free -h
   cat /proc/meminfo
   ```

2. **プロセスのメモリ使用量確認**
   ```bash
   ps aux --sort=-%mem
   ```

3. **メモリのクリーンアップ**
   ```bash
   python -c "import gc; gc.collect()"
   ```

4. **システムメモリの増設**
   - 物理メモリの増設
   - スワップファイルの設定

### 6. セキュリティの問題

#### 問題: ファイル権限エラー

**症状**:
```
PermissionError: [Errno 13] Permission denied
OSError: [Errno 1] Operation not permitted
```

**原因**:
- ファイル権限が不適切
- 所有者が間違っている
- SELinuxの設定
- ディレクトリの権限

**解決方法**:
1. **ファイル権限の確認**
   ```bash
   ls -la src/config/config.yaml
   ls -la .env
   ```

2. **権限の修正**
   ```bash
   chmod 644 src/config/config.yaml
   chmod 600 .env
   chmod 755 logs/
   ```

3. **所有者の修正**
   ```bash
   chown $USER:$USER src/config/config.yaml
   chown $USER:$USER .env
   ```

#### 問題: セキュリティ監査で問題が発見された

**症状**:
- セキュリティスコアが低い
- 脆弱性が発見された
- 設定が不適切

**原因**:
- デフォルト設定の使用
- 権限の緩い設定
- 機密情報の露出
- 依存関係の脆弱性

**解決方法**:
1. **セキュリティ監査の実行**
   ```bash
   python scripts/security_enhancer.py
   ```

2. **推奨事項の確認**
   - 監査レポートを確認
   - 推奨事項を実装

3. **設定の修正**
   - ファイル権限の修正
   - 機密情報の保護
   - 依存関係の更新

## 予防策

### 1. 定期メンテナンス

#### 日次
- ログファイルの確認
- システムリソースの確認
- エラーメッセージの確認

#### 週次
- パフォーマンス監視
- セキュリティ監査
- バックアップの確認

#### 月次
- システムアップデート
- 依存関係の更新
- 設定の見直し

### 2. 監視の設定

#### システム監視
```bash
# 監視スクリプトの設定
crontab -e
*/5 * * * * /path/to/monitor_chimera.sh
```

#### ログ監視
```bash
# ログローテーションの設定
sudo cp chimera.logrotate /etc/logrotate.d/chimera
```

#### アラート設定
- Discord通知の設定
- メール通知の設定
- SMS通知の設定

### 3. バックアップ

#### 自動バックアップ
```bash
# バックアップスクリプトの設定
crontab -e
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

### 3. 外部サポート

#### IB証券サポート
- 電話: 03-4588-8000
- メール: support@interactivebrokers.com
- ウェブサイト: https://www.interactivebrokers.com

#### Discordサポート
- Discord公式サポート
- サーバー管理者
- コミュニティフォーラム

## 免責事項

- このガイドは一般的な問題と解決方法を提供しています
- すべての問題が解決されることを保証するものではありません
- システムの変更は自己責任で行ってください
- 重要な設定変更前には必ずバックアップを取ってください
- 不明な場合は専門家に相談してください
