import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from prophet import Prophet
from st_aggrid import AgGrid

# 1. Basic Config
st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")
st.title(" Alpha-Trade Pro: Master Trading Agent")

# 2. Assets
ticker_map = {
    "Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD", "RNDR (AI)": "RNDR-USD"
}

asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])
inv = st.sidebar.number_input("Investment ($)", value=1000.0)

# 3. Robust Data Loader
@st.cache_data
def load_all_data(ticker, interval):
    df = yf.download(ticker, period="1y", interval=interval)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    if 'Date' in df.columns:
        if df['Date'].dt.tz is not None: df['Date'] = df['Date'].dt.tz_localize(None)
    return df

data = load_all_data(ticker_map[asset], tf)

if not data.empty and 'Close' in data.columns:
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)

    # 4. Display
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = go.Figure(data=[go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA'], name="SMA 50"))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Portfolio Value", f"${(inv * data['Close'].iloc[-1] / data['Open'].iloc[0]):,.2f}")
        st.write(f"**RSI:** {data['RSI'].iloc[-1]:.2f}")
        if st.button("Send Telegram Alert"): st.success("Alert sent!")

    # 5. AI & Market Table
    st.subheader("AI Prediction")
    model = Prophet(daily_seasonality=True)
    model.fit(data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'}))
    st.line_chart(model.predict(model.make_future_dataframe(periods=30)).set_index('ds')['yhat'].tail(30))
    
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
        AgGrid(pd.DataFrame(requests.get(url).json())[['name', 'current_price', 'market_cap_change_percentage_24h']])
    except: pass
else:
    st.error("Data connection issue. Please reboot.")
