import numpy as np


def run_backtest(df):

    df = df.copy()

    if 'EMA20' not in df.columns:
        return {"error": "EMA20 missing"}

    if 'EMA50' not in df.columns:
        return {"error": "EMA50 missing"}

    # Market Return
    df['Returns'] = df['Close'].pct_change()

    # EMA Strategy
    df['Signal'] = np.where(
        df['EMA20'] > df['EMA50'],
        1,
        0
    )

    df['Strategy'] = (
        df['Signal'].shift(1) * df['Returns']
    )

    market_return = (
        (1 + df['Returns']).cumprod().iloc[-1]
    )

    strategy_return = (
        (1 + df['Strategy']).cumprod().iloc[-1]
    )

    return {
        "market_return": round(float(market_return), 2),
        "strategy_return": round(float(strategy_return), 2)
    }
