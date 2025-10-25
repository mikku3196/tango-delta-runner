import argparse
from src.bots.satellite_range_bot import SatelliteRangeBot
from src.backtesting.backtest_engine import BacktestEngine

def main():
    # --- argparse の設定 ---
    parser = argparse.ArgumentParser(description="Project Chimera Backtest Runner")
    parser.add_argument('--ticker', type=str, default='7203.T', help='Stock ticker symbol')
    parser.add_argument('--start', type=str, default='2022-01-01', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2024-12-31', help='End date (YYYY-MM-DD)')
    parser.add_argument('--capital', type=int, default=1000000, help='Initial capital')
    parser.add_argument('--sl', type=float, default=0.02, help='Stop loss percentage (e.g., 0.05 for 5%)')
    parser.add_argument('--tsl', type=float, default=0.08, help='Trailing stop loss percentage (e.g., 0.08 for 8%)')
    parser.add_argument('--bb_period', type=int, default=20, help='Bollinger Bands period')
    parser.add_argument('--bb_std', type=float, default=2.0, help='Bollinger Bands standard deviation')
    
    args = parser.parse_args()

    print("="*80)
    print("Project Chimera バックテスト実行")
    print("="*80)

    # Botの初期化時にコマンドライン引数を渡す
    bot = SatelliteRangeBot(
        stop_loss_percentage=args.sl,
        trailing_stop_percentage=args.tsl,
        bollinger_period=args.bb_period,
        bollinger_std_dev=args.bb_std
    )

    # BacktestEngineの初期化時も同様
    engine = BacktestEngine(
        strategy=bot,
        ticker=args.ticker,
        start_date=args.start,
        end_date=args.end,
        initial_capital=args.capital
    )

    print(f"{bot.name} を初期化中...")
    print(f"BacktestEngine を初期化中...")
    print(f"対象銘柄: {args.ticker}")
    print(f"期間: {args.start} ～ {args.end}")
    print(f"初期資金: {args.capital:,}円")
    # --- パラメータも表示 ---
    print(f"ストップロス: {args.sl*100:.2f}%")
    print(f"トレーリングストップ: {args.tsl*100:.2f}%")
    print(f"BB期間: {args.bb_period}日")
    print(f"BB標準偏差: {args.bb_std}σ")
    print("="*80)

    # バックテストを実行（データは__init__で既に読み込み済み）
    results = engine.run()
    
    # 結果を表示
    print(f"\n=== バックテスト結果 ===")
    print(f"戦略: {results['strategy']}")
    print(f"銘柄: {results['ticker']}")
    print(f"期間: {results['start_date']} - {results['end_date']}")
    print(f"初期資金: {results['initial_capital']:,}円")
    print(f"最終資産: {results['final_value']:,.0f}円")
    print(f"総リターン: {results['total_return']:.2%}")
    print(f"年率リターン: {results['annual_return']:.2%}")
    print(f"最大ドローダウン: {results['max_drawdown']:.2%}")
    print(f"シャープレシオ: {results['sharpe_ratio']:.2f}")
    print(f"取引回数: {results['total_trades']}")
    print(f"勝率: {results['win_rate']:.2%}")
    
    # パラメータ設定も表示
    print(f"\n=== 使用パラメータ ===")
    print(f"ストップロス率: {args.sl*100:.2f}%")
    print(f"トレーリングストップ率: {args.tsl*100:.2f}%")
    print(f"ボリンジャーバンド期間: {args.bb_period}日")
    print(f"ボリンジャーバンド標準偏差: {args.bb_std}σ")

if __name__ == "__main__":
    main()