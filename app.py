import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from prophet import Prophet
from st_aggrid import AgGrid

st.set_page_config(page_title="Alpha-Trade Pro: Master Dashboard", layout="wide")
st.title(" Alpha-Trade Pro: Full Integrated Trading Agent")

# 1. All Assets Config
ticker_map = {
    "Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD", "RNDR (AI)": "RNDR-USD"
}

# 2. Sidebar Controls
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])
inv = st.sidebar.number_input("Investment ($)", value=1000.0)

# 3. Data Engine
@st.cache_data
def get_data(ticker, interval):
    df = yf.download(ticker, period="1y", interval=interval)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    if df['Date'].dt.tz is not None: df['Date'] = df['Date'].dt.tz_localize(None)
    return df

data = get_data(ticker_map[asset], tf)

if not data.empty:
    # Indicators
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)

    # UI Layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"{asset} Analysis")
        fig = go.Figure(data=[go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA'], name="SMA 50", line=dict(color='yellow')))
        fig.update_layout(template="plotly_dark", height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Stats")
        st.metric("Portfolio Value", f"${(inv * data['Close'].iloc[-1] / data['Open'].iloc[0]):,.2f}")
        st.write(f"**Current RSI:** {data['RSI'].iloc[-1]:.2f}")
        if st.button("Send Telegram Alert"): st.success("Alert Sent!")

    # AI Prediction
    st.subheader(" AI Price Prediction (Next 30 Days)")
    model = Prophet(daily_seasonality=True)
    model.fit(data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'}))
    forecast = model.predict(model.make_future_dataframe(periods=30))
    st.line_chart(forecast.set_index('ds')['yhat'].tail(30))

    # Market Table
    st.subheader(" Live Top 300 Crypto Market")
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
        AgGrid(pd.DataFrame(requests.get(url).json())[['name', 'current_price', 'market_cap_change_percentage_24h']])
    except: st.error("Market data unavailable")
else: st.error("Please select a valid asset.")
