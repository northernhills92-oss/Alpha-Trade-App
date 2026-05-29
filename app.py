import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta

st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")
st.title("Alpha-Trade Pro: Advanced Trading Agent")

ticker_map = {"Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F", "Bitcoin": "BTC-USD"}

asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1mo", "1wk", "1d", "4h", "1h"])

data = yf.download(ticker_map[asset], period="1y", interval=tf)

# Column handling
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# Indicators using 'ta' library
data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)

# Chart
fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
fig.update_layout(title=f"{asset} Candlestick Chart", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# Analysis
current_rsi = data['RSI'].iloc[-1]
st.write(f"### Current RSI: {current_rsi:.2f}")

if current_rsi < 30:
    st.success("Buy Signal: RSI Oversold!")
elif current_rsi > 70:
    st.error("Sell Signal: RSI Overbought!")
