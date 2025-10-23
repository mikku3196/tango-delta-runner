import yfinance as yf

ticker_symbol = "7203.T"

print("="*50)
print(f"--- FINAL TEST ---")
print(f"Attempting to download data directly for: '{ticker_symbol}'")
print("="*50)

try:
    # yfinanceを、最もシンプルな形で直接呼び出す
    data = yf.download(ticker_symbol, start="2022-01-01", end="2024-12-31")
    
    # データが空かどうかをチェック
    if data.empty:
        print("\n--- RESULT ---")
        print("Data is empty. yfinance failed to retrieve data for some reason.")
        print("This confirms the issue is likely within the yfinance library itself.")
    else:
        print("\n--- RESULT ---")
        print("SUCCESS! Data downloaded successfully.")
        print("This means the issue is a complex interaction with our BacktestEngine.")
        print("\nFirst 5 rows of data:")
        print(data.head())

except Exception as e:
    print(f"\n--- ERROR ---")
    print(f"An error occurred: {e}")
    print("This likely confirms the issue is within the yfinance library itself.")