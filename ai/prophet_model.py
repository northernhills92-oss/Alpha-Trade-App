from prophet import Prophet


def prophet_signal(df):

    model_df = df[['Date', 'Close']].rename(
        columns={
            'Date': 'ds',
            'Close': 'y'
        }
    )

    model = Prophet(
        daily_seasonality=True,
        changepoint_prior_scale=0.05
    )

    model.fit(model_df)

    future = model.make_future_dataframe(periods=24)

    forecast = model.predict(future)

    current = forecast['yhat'].iloc[-2]
    future_price = forecast['yhat'].iloc[-1]

    if future_price > current:
        return "BUY"

    return "SELL"
