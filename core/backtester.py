import numpy as np


def run_backtest(df):

    df['Returns'] = df['Close'].pct_change()

    df['Strategy'] = np.where(
        df['Signal'].str.contains("BUY"),
        df['Returns'],
        0
    )

    market = (1 + df['Returns']).cumprod()
    strategy = (1 + df['Strategy']).cumprod()

    final_market = market.iloc[-1]
    final_strategy = strategy.iloc[-1]

    return {
        "market_return": round(final_market, 2),
        "strategy_return": round(final_strategy, 2)
    }
