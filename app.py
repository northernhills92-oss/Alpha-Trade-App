import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from prophet import Prophet
from st_aggrid import AgGrid

st.set_page_config(page_title="Alpha-Trade Pro: Master Dashboard", layout="wide")
st.title("🚀 Alpha-Trade Pro: Full Integrated Trading Agent")

# 1. Assets Configuration (Commodities & Crypto)
ticker_map = {
    "Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD", "RNDR (AI)": "RNDR-USD"
}

# 2. Sidebar
asset_name = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])

# 3. Fetching Market Data
data = yf.download(ticker_map[asset_name], period="1y", interval=tf)
data.reset_index(inplace=True)
if data['Date'].dt.tz is not None:
    data['Date'] = data['Date'].dt.tz_localize(None)

# 4. Technical Analysis
data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{asset_name} Analysis")
    fig = go.Figure(data=[go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("AI Price Prediction")
    model = Prophet(daily_seasonality=True)
    model.fit(data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'}))
    forecast = model.predict(model.make_future_dataframe(periods=30))
    st.line_chart(forecast.set_index('ds')['yhat'])

# 5. Live Market Overview (Top 100 Crypto API)
st.subheader("🌍 Live Market Overview (Top 100)")
try:
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    response = requests.get(url).json()
    df_market = pd.DataFrame(response)
    AgGrid(df_market[['name', 'symbol', 'current_price', 'market_cap_change_percentage_24h']])
except:
    st.error("Market data temporarily unavailable.")
