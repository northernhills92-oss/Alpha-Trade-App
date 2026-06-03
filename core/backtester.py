import numpy as np


def run_backtest(df):

    if 'EMA20' not in df.columns or 'EMA50' not in df.columns:
        return {
            "market_return": 0,
            "strategy_return": 0
        }

    df = df.copy()

    df['Returns'] = df['Close'].pct_change()

    df['Signal'] = np.where(
        df['EMA20'] > df['EMA50'],
        "BUY",
        "SELL"
    )

    df['Strategy'] = np.where(
        df['Signal'] == "BUY",
        df['Returns'],
        0
    )

    market = (1 + df['Returns']).cumprod()
    strategy = (1 + df['Strategy']).cumprod()

    return {
        "market_return": round(float(market.iloc[-1]), 2),
        "strategy_return": round(float(strategy.iloc[-1]), 2)
    }
