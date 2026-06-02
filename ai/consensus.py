from ai.xgboost_model import xgb_signal

def consensus_signal(df):

    signals = []

    # Prophet temporarily disabled
    # signals.append(prophet_signal(df))

    signals.append(xgb_signal(df))

    buy_count = signals.count("BUY")
    sell_count = signals.count("SELL")

    if buy_count >= 1:
        return "STRONG BUY"

    if sell_count >= 1:
        return "STRONG SELL"

    return "HOLD"
