import yfinance as yf
import pandas as pd


def load_data(symbol, interval="1h"):

    df = yf.download(
        symbol,
        period="6mo",
        interval=interval,
        auto_adjust=True
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    if 'Datetime' in df.columns:
        df.rename(columns={'Datetime': 'Date'}, inplace=True)

    # Force UTC then remove timezone
    df['Date'] = pd.to_datetime(
        df['Date'],
        utc=True
    ).dt.tz_localize(None)

    return df
