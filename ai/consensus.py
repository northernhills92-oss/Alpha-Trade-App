from ai.prophet_model import prophet_signal
from ai.xgboost_model import xgb_signal


def consensus_signal(df):

    signals = []

    signals.append(prophet_signal(df))
    signals.append(xgb_signal(df))

    buy_count = signals.count("BUY")
    sell_count = signals.count("SELL")

    if buy_count >= 2:
        return "STRONG BUY"

    if sell_count >= 2:
        return "STRONG SELL"

    return "HOLD"
