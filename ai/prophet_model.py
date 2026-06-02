from prophet import Prophet
import pandas as pd

def prophet_signal(df):

    if 'Date' not in df.columns:
        return "HOLD"

    model_df = df[['Date', 'Close']].copy()

    model_df.columns = ['ds', 'y']

    model_df['ds'] = pd.to_datetime(model_df['ds'])

    model_df = model_df.dropna()

    if len(model_df) < 50:
        return "HOLD"

    model = Prophet(
        daily_seasonality=True,
        changepoint_prior_scale=0.05
    )

    model.fit(model_df)

    future = model.make_future_dataframe(periods=24)

    forecast = model.predict(future)

    current = forecast['yhat'].iloc[-2]
    future_price = forecast['yhat'].iloc[-1]

    return "BUY" if future_price > current else "SELL"
