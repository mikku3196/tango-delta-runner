#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Chimera - SatelliteRangeBot Strategy Backtest
"""

import pandas as pd
import yfinance as yf

def main():
    print("=" * 80)
    print("🚀 Project Chimera - SatelliteRangeBot Strategy Backtest")
    print("=" * 80)
    
    # データを読み込み
    print("📥 Loading Toyota (7203.T) data from 2022-01-01 to 2024-12-31...")
    ticker = yf.Ticker("7203.T")
    data = ticker.history(start="2022-01-01", end="2024-12-31")
    print(f"✅ Data loaded: {len(data)} days")
    
    # ボリンジャーバンドを計算
    print("🔧 Calculating Bollinger Bands...")
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    data['BB_Std'] = data['Close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (data['BB_Std'] * 2.0)
    data['BB_Lower'] = data['BB_Middle'] - (data['BB_Std'] * 2.0)
    data = data.ffill()
    print("✅ Bollinger Bands calculated")
    
    # レンジ取引戦略を実行
    print("🔄 Running range trading strategy...")
    cash = 1000000  # 初期資金100万円
    shares = 0
    trades = []
    
    for i, row in data.iterrows():
        if pd.isna(row['BB_Upper']) or pd.isna(row['BB_Lower']):
            continue
            
        # 買いシグナル：価格が下限バンドを下回った時
        if row['Close'] < row['BB_Lower'] and cash > 0:
            shares_to_buy = cash / row['Close']
            shares += shares_to_buy
            cash = 0
            trades.append(('BUY', row['Close'], shares_to_buy))
            
        # 売りシグナル：価格が上限バンドを上回った時
        elif row['Close'] > row['BB_Upper'] and shares > 0:
            cash = shares * row['Close']
            shares = 0
            trades.append(('SELL', row['Close'], shares))
    
    # 最終的なポートフォリオ価値を計算
    final_value = cash + (shares * data['Close'].iloc[-1])
    total_return = (final_value - 1000000) / 1000000
    
    # 結果を表示
    print("=" * 80)
    print("📊 バックテスト結果")
    print("=" * 80)
    
    print(f"戦略: SatelliteRangeBot (Bollinger Bands)")
    print(f"銘柄: 7203.T (Toyota)")
    print(f"期間: 2022-01-01 ～ 2024-12-31")
    print()
    
    print("💰 パフォーマンス指標:")
    print(f"  初期資金: ¥1,000,000")
    print(f"  最終資産: ¥{final_value:,.0f}")
    print(f"  総リターン: {total_return:.2%}")
    print()
    
    print("📈 取引統計:")
    print(f"  総取引回数: {len(trades)}")
    
    # 取引履歴の詳細
    if trades:
        print("📋 取引履歴:")
        print("-" * 60)
        for i, (action, price, amount) in enumerate(trades):
            action_emoji = "🟢 買い" if action == 'BUY' else "🔴 売り"
            print(f"  {i+1:2d}. {action_emoji} | ¥{price:,.0f} | {amount:.2f}株")
        print()
    
    print("✅ バックテストが正常に完了しました")
    
    # 買い持ち戦略との比較
    buy_hold_return = (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]
    print("=" * 80)
    print("📊 戦略比較")
    print("=" * 80)
    print(f"レンジ取引戦略: {total_return:.2%}")
    print(f"買い持ち戦略:   {buy_hold_return:.2%}")
    print(f"差額:          {(total_return - buy_hold_return):.2%}")
    
    if total_return > buy_hold_return:
        print("🎉 レンジ取引戦略が買い持ち戦略を上回りました！")
    else:
        print("📉 レンジ取引戦略は買い持ち戦略を下回りました")

if __name__ == "__main__":
    main()
