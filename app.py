import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import pandas_ta as ta

st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")
st.title("Alpha-Trade Pro: Advanced Trading Agent")

# Assets
ticker_map = {"Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F", "Bitcoin": "BTC-USD"}

# Sidebar
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1mo", "1wk", "1d", "4h", "1h"])

# Data
df = yf.download(ticker_map[asset], period="1y", interval=tf)

# Indicators
df['RSI'] = ta.rsi(df['Close'], length=14)
df['SMA'] = ta.sma(df['Close'], length=50)

# Chart
fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
fig.update_layout(title=f"{asset} Candlestick Chart", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# Analysis
st.write(f"### Current RSI: {df['RSI'].iloc[-1]:.2f}")
if df['RSI'].iloc[-1] < 30:
    st.success("Buy Signal: RSI Oversold!")
elif df['RSI'].iloc[-1] > 70:
    st.error("Sell Signal: RSI Overbought!")
