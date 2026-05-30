import ta


def add_indicators(df):

    df['RSI'] = ta.momentum.RSIIndicator(
        close=df['Close'],
        window=14
    ).rsi()

    df['EMA20'] = ta.trend.EMAIndicator(
        close=df['Close'],
        window=20
    ).ema_indicator()

    df['EMA50'] = ta.trend.EMAIndicator(
        close=df['Close'],
        window=50
    ).ema_indicator()

    macd = ta.trend.MACD(close=df['Close'])

    df['MACD'] = macd.macd()
    df['MACD_SIGNAL'] = macd.macd_signal()

    return df
