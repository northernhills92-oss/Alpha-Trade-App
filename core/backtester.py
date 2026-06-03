import numpy as np


def run_backtest(df):

    df = df.copy()

    if 'EMA20' not in df.columns:
        return {"error": "EMA20 missing"}

    if 'EMA50' not in df.columns:
        return {"error": "EMA50 missing"}

    df['Returns'] = df['Close'].pct_change()

    df['Signal'] = np.where(
        df['EMA20'] > df['EMA50'],
        1,
        0
    )

    df['Strategy'] = (
        df['Signal'].shift(1).fillna(0)
        * df['Returns']
    )

    market_return = (
        (1 + df['Returns'].fillna(0))
        .cumprod()
        .iloc[-1]
    )

    strategy_return = (
        (1 + df['Strategy'].fillna(0))
        .cumprod()
        .iloc[-1]
    )

    return {
        "market_return_%": round((market_return - 1) * 100, 2),
        "strategy_return_%": round((strategy_return - 1) * 100, 2)
    }
