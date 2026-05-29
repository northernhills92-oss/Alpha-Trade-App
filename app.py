import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from prophet import Prophet
from st_aggrid import AgGrid

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(page_title="Alpha-Trade Pro X", layout="wide")
st.title("🚀 Alpha-Trade Pro X")

# =========================================
# SETTINGS
# =========================================

ticker_map = {
    "Gold": "GC=F",
    "Oil": "CL=F",
    "Silver": "SI=F",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "RNDR": "RNDR-USD"
}

interval_map = {
    "1d": "1d",
    "1h": "1h",
    "15m": "15m"
}

asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", list(interval_map.keys()))
investment = st.sidebar.number_input("Investment ($)", value=1000.0)

risk_percent = st.sidebar.slider("Risk % Per Trade", 1, 10, 2)

# =========================================
# DATA LOADER
# =========================================

@st.cache_data
def load_data(symbol, interval):
    try:
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

        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

        return df

    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

data = load_data(ticker_map[asset], interval_map[tf])

# =========================================
# MAIN APP
# =========================================

if not data.empty:

    # =====================================
    # INDICATORS
    # =====================================

    data['RSI'] = ta.momentum.RSIIndicator(
        close=data['Close'],
        window=14
    ).rsi()

    data['SMA50'] = ta.trend.SMAIndicator(
        close=data['Close'],
        window=50
    ).sma_indicator()

    data['EMA20'] = ta.trend.EMAIndicator(
        close=data['Close'],
        window=20
    ).ema_indicator()

    macd = ta.trend.MACD(close=data['Close'])

    data['MACD'] = macd.macd()
    data['MACD_SIGNAL'] = macd.macd_signal()

    # =====================================
    # SIGNAL ENGINE
    # =====================================

    def signal_strategy(row):

        if (
            row['RSI'] < 35 and
            row['Close'] > row['SMA50'] and
            row['MACD'] > row['MACD_SIGNAL']
        ):
            return "BUY"

        elif (
            row['RSI'] > 70 and
            row['MACD'] < row['MACD_SIGNAL']
        ):
            return "SELL"

        return "HOLD"

    data['Signal'] = data.apply(signal_strategy, axis=1)

    latest_signal = data['Signal'].iloc[-1]

    # =====================================
    # RISK MANAGEMENT
    # =====================================

    current_price = data['Close'].iloc[-1]

    stop_loss = current_price * 0.97
    take_profit = current_price * 1.06

    risk_amount = investment * (risk_percent / 100)

    position_size = risk_amount / abs(current_price - stop_loss)

    # =====================================
    # CHART
    # =====================================

    col1, col2 = st.columns([3, 1])

    with col1:

        fig = go.Figure()

        fig.add_trace(
            go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candles"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data['SMA50'],
                name="SMA50"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data['EMA20'],
                name="EMA20"
            )
        )

        fig.update_layout(height=700)

        st.plotly_chart(fig, use_container_width=True)

    # =====================================
    # SIDE PANEL
    # =====================================

    with col2:

        pnl = (
            investment *
            (current_price / data['Open'].iloc[0])
        )

        st.metric(
            "Portfolio Value",
            f"${pnl:,.2f}"
        )

        st.metric("Current Signal", latest_signal)

        st.write(f"### RSI: {data['RSI'].iloc[-1]:.2f}")

        st.write(f"### Stop Loss: ${stop_loss:.2f}")

        st.write(f"### Take Profit: ${take_profit:.2f}")

        st.write(f"### Position Size: {position_size:.4f}")

    # =====================================
    # AI FORECAST
    # =====================================

    st.subheader("🤖 AI Forecast")

    prophet_df = data[['Date', 'Close']].rename(
        columns={
            'Date': 'ds',
            'Close': 'y'
        }
    )

    model = Prophet(
        daily_seasonality=True,
        changepoint_prior_scale=0.05
    )

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=30)

    forecast = model.predict(future)

    st.line_chart(
        forecast.set_index('ds')['yhat'].tail(30)
    )

    # =====================================
    # BACKTEST
    # =====================================

    st.subheader("📊 Strategy Backtest")

    data['Returns'] = data['Close'].pct_change()

    data['Strategy_Returns'] = np.where(
        data['Signal'] == "BUY",
        data['Returns'],
        0
    )

    cumulative_market = (
        (1 + data['Returns']).cumprod()
    )

    cumulative_strategy = (
        (1 + data['Strategy_Returns']).cumprod()
    )

    bt = pd.DataFrame({
        'Market': cumulative_market,
        'Strategy': cumulative_strategy
    })

    st.line_chart(bt)

    # =====================================
    # TELEGRAM ALERT
    # =====================================

    st.subheader("📨 Telegram Alerts")

    TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"

    def send_telegram(msg):

        url = (
            f"https://api.telegram.org/bot"
            f"{TELEGRAM_TOKEN}/sendMessage"
        )

        payload = {
            "chat_id": CHAT_ID,
            "text": msg
        }

        try:
            requests.post(url, data=payload)

        except:
            pass

    if st.button("Send Telegram Alert"):

        send_telegram(
            f"{asset} Signal: {latest_signal}\n"
            f"Price: ${current_price:.2f}"
        )

        st.success("Telegram Alert Sent")

    # =====================================
    # TOP CRYPTO TABLE
    # =====================================

    st.subheader("🌍 Global Top 100 Crypto")

    try:

        url = (
            "https://api.coingecko.com/api/v3/"
            "coins/markets"
            "?vs_currency=usd"
            "&order=market_cap_desc"
            "&per_page=100&page=1"
        )

        crypto = pd.DataFrame(
            requests.get(url).json()
        )

        table = crypto[
            [
                'name',
                'symbol',
                'current_price',
                'market_cap_rank',
                'price_change_percentage_24h'
            ]
        ]

        AgGrid(table)

    except Exception as e:

        st.warning(f"CoinGecko Error: {e}")

else:

    st.error("No market data loaded.")
