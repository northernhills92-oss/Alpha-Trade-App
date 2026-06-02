from prophet import Prophet
import pandas as pd


def prophet_signal(df):

    try:

        # Required columns check
        if 'Date' not in df.columns:
            return "HOLD"

        if 'Close' not in df.columns:
            return "HOLD"

        # Prepare Prophet dataframe
        model_df = df[['Date', 'Close']].copy()

        model_df.columns = ['ds', 'y']

        # Convert to datetime
        model_df['ds'] = pd.to_datetime(model_df['ds'])

        # Remove timezone (IMPORTANT)
        if model_df['ds'].dt.tz is not None:
            model_df['ds'] = model_df['ds'].dt.tz_localize(None)

        # Remove missing values
        model_df = model_df.dropna()

        # Need enough data
        if len(model_df) < 30:
            return "HOLD"

        # Build model
        model = Prophet(
            daily_seasonality=True,
            changepoint_prior_scale=0.05
        )

        model.fit(model_df)

        # Predict next 24 periods
        future = model.make_future_dataframe(
            periods=24
        )

        forecast = model.predict(future)

        current_prediction = forecast['yhat'].iloc[-2]
        future_prediction = forecast['yhat'].iloc[-1]

        if future_prediction > current_prediction:
            return "BUY"

        elif future_prediction < current_prediction:
            return "SELL"

        return "HOLD"

    except Exception as e:

        print(f"Prophet Error: {e}")

        return "HOLD"
