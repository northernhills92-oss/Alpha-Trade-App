import pandas as pd
from datetime import datetime


LOG_FILE = "trade_journal.csv"


def log_trade(asset, signal, price):

    row = {
        "time": datetime.now(),
        "asset": asset,
        "signal": signal,
        "price": price
    }

    try:
        df = pd.read_csv(LOG_FILE)

    except:
        df = pd.DataFrame()

    df = pd.concat([
        df,
        pd.DataFrame([row])
    ])

    df.to_csv(LOG_FILE, index=False)
