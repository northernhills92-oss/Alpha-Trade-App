import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from st_aggrid import AgGrid # interactive table အတွက်

st.set_page_config(page_title="Alpha-Trade Pro v2", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .main {background-color: #0e1117;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Alpha-Trade Pro: Professional Dashboard")

# 1. Advanced Sidebar
asset = st.sidebar.selectbox("Select Asset", ["Gold", "Oil", "BTC", "ETH", "FET (AI)"])
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])
show_macd = st.sidebar.checkbox("Show MACD")

# 2. Data Loading (Interactive)
data = yf.download("BTC-USD", period="1y", interval="1d")

# 3. Interactive Table using AgGrid
st.subheader("Market Data Explorer")
AgGrid(data.tail(10)) 

# 4. Professional Charting
fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])

if show_macd:
    macd = ta.trend.MACD(data['Close'])
    fig.add_trace(go.Scatter(x=data.index, y=macd.macd(), name="MACD"))

fig.update_layout(template="plotly_dark", title=f"{asset} Professional Chart")
st.plotly_chart(fig, use_container_width=True)

# 5. Portfolio Status
st.sidebar.subheader("Portfolio Tracker")
investment = st.sidebar.number_input("Enter your investment ($)")
current_price = data['Close'].iloc[-1]
st.sidebar.write(f"Current Value: ${investment * current_price / data['Open'].iloc[0]:.2f}")
