import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests

st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")
st.title("Alpha-Trade Pro: Full Trading Agent")

# Telegram function
def send_telegram(msg):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")
    except:
        st.warning("Telegram settings not configured correctly.")

# Assets
ticker_map = {"Gold": "GC=F", "Oil": "CL=F", "Bitcoin": "BTC-USD", "Fetch.ai": "FET-USD"}
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))

# Data Fetching
data = yf.download(ticker_map[asset], period="6mo", interval="1d")

# --- အဓိကပြင်ဆင်ချက် ---
if data.empty or 'Close' not in data.columns:
    st.error("Data fetch failed. Please check the asset or try another timeframe.")
else:
    # MultiIndex handling
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Pivot calculation
    high_prev = data['High'].iloc[-2]
    low_prev = data['Low'].iloc[-2]
    close_prev = data['Close'].iloc[-2]
    pivot = (high_prev + low_prev + close_prev) / 3
    support = (pivot * 2) - high_prev
    resistance = (pivot * 2) - low_prev

    # Indicators
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="Support")
    fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="Resistance")
    st.plotly_chart(fig, use_container_width=True)

    # Signal
    rsi_val = data['RSI'].iloc[-1]
    st.write(f"### Current RSI: {rsi_val:.2f} | Support: {support:.2f} | Resistance: {resistance:.2f}")

    if rsi_val < 30:
        msg = f"BUY ALERT: {asset} is oversold at {data['Close'].iloc[-1]:.2f}"
        st.success(msg)
        if st.button("Send Telegram Alert"):
            send_telegram(msg)
