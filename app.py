import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from prophet import Prophet
from st_aggrid import AgGrid

# Page Config
st.set_page_config(page_title="Alpha-Trade Pro X - Pro Version", layout="wide")
st.title("🚀 Alpha-Trade Pro X - Advanced Strategy")

# Assets & Config
ticker_map = {"Gold": "GC=F", "Oil": "CL=F", "BTC": "BTC-USD", "ETH": "ETH-USD"}
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
investment = st.sidebar.number_input("Investment ($)", value=1000.0)

# Data Loader (Multi-Timeframe Logic)
@st.cache_data
def load_data(symbol, interval):
    df = yf.download(symbol, period="6mo", interval=interval, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    if 'Datetime' in df.columns: df.rename(columns={'Datetime': 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    return df

data = load_data(ticker_map[asset], "1h")      # Main TF
data_htf = load_data(ticker_map[asset], "1d")  # Higher TF for Trend Filter

# Indicators
data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
data['SMA50'] = ta.trend.sma_indicator(data['Close'], window=50)
data_htf['SMA50'] = ta.trend.sma_indicator(data_htf['Close'], window=50)

# Confluence Strategy (1h Trend must match 1d Trend)
def signal_strategy(row, htf_trend):
    if row['RSI'] < 35 and row['Close'] > row['SMA50'] and htf_trend == "UP":
        return "BUY"
    elif row['RSI'] > 65:
        return "SELL"
    return "HOLD"

htf_trend = "UP" if data_htf['Close'].iloc[-1] > data_htf['SMA50'].iloc[-1] else "DOWN"
data['Signal'] = data.apply(lambda row: signal_strategy(row, htf_trend), axis=1)

# Trailing Stop Loss Logic
current_price = data['Close'].iloc[-1]
trailing_sl = current_price * 0.95 # 5% Trail
st.write(f"**Market Context:** {htf_trend} Trend detected from Higher Timeframe.")
st.write(f"**Trailing Stop Loss Level:** ${trailing_sl:.2f}")

# Main Visuals
col1, col2 = st.columns([3, 1])
with col1:
    fig = go.Figure(data=[go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Current Signal", data['Signal'].iloc[-1])
    if st.button("Send Telegram Alert"):
        requests.post(f"https://api.telegram.org/botYOUR_TOKEN/sendMessage", 
                      data={"chat_id": "YOUR_CHAT_ID", "text": f"Signal: {data['Signal'].iloc[-1]} for {asset}"})

# AI Forecast & Backtest
st.subheader("🤖 AI Forecast & Backtest")
m = Prophet().fit(data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'}))
st.line_chart(m.predict(m.make_future_dataframe(periods=10)).set_index('ds')['yhat'].tail(10))
