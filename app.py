import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests

st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")
st.title("Alpha-Trade Pro: Full Trading Agent")

# Telegram Bot Setup (Secrets ထဲတွင် ထည့်ထားရန်)
def send_telegram(msg):
    token = st.secrets["TELEGRAM_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")

# Assets
ticker_map = {"Gold": "GC=F", "Oil": "CL=F", "Bitcoin": "BTC-USD", "Fetch.ai": "FET-USD"}
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))

# Data & Pivot Points
data = yf.download(ticker_map[asset], period="6mo", interval="1d")
pivot = (data['High'].iloc[-2] + data['Low'].iloc[-2] + data['Close'].iloc[-2]) / 3
support = (pivot * 2) - data['High'].iloc[-2]
resistance = (pivot * 2) - data['Low'].iloc[-2]

# Indicators
data['RSI'] = ta.momentum.rsi(data['Close'], window=14)

# Chart
fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="Support")
fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="Resistance")
st.plotly_chart(fig, use_container_width=True)

# Signal & Alert
rsi_val = data['RSI'].iloc[-1]
st.write(f"### RSI: {rsi_val:.2f} | Support: {support:.2f} | Resistance: {resistance:.2f}")

if rsi_val < 30:
    msg = f"BUY ALERT: {asset} is oversold at {data['Close'].iloc[-1]:.2f}"
    st.success(msg)
    if st.button("Send Telegram Alert"):
        send_telegram(msg)
