import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from st_aggrid import AgGrid

st.set_page_config(page_title="Alpha-Trade Pro v2", layout="wide")
st.title("🚀 Alpha-Trade Pro: Professional Dashboard")

# Assets
ticker_map = {"Gold": "GC=F", "Oil": "CL=F", "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD"}
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])
show_macd = st.sidebar.checkbox("Show MACD Indicator")

# Data
@st.cache_data
def get_data(ticker, interval="1d"):
    return yf.download(ticker, period="1y", interval=interval)

data = get_data(ticker_map[asset], interval=tf)

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # UI: Interactive Data
    st.subheader("Market Data Explorer")
    AgGrid(data.tail(10))

    # UI: Professional Chart
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    if show_macd:
        macd = ta.trend.MACD(data['Close'])
        fig.add_trace(go.Scatter(x=data.index, y=macd.macd(), name="MACD", line=dict(color='cyan')))
    
    fig.update_layout(template="plotly_dark", title=f"{asset} Professional Analysis")
    st.plotly_chart(fig, use_container_width=True)

    # UI: Portfolio
    st.sidebar.subheader("Portfolio Tracker")
    inv = st.sidebar.number_input("Investment ($)", value=1000.0)
    if data['Open'].iloc[0] > 0:
        val = (inv * data['Close'].iloc[-1]) / data['Open'].iloc[0]
        st.sidebar.metric("Estimated Portfolio Value", f"${val:,.2f}")
else:
    st.error("Data not available.")
