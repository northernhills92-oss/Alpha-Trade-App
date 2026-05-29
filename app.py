import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests
from prophet import Prophet
from st_aggrid import AgGrid

st.set_page_config(page_title="Alpha-Trade Pro: Master Dashboard", layout="wide")
st.title("🚀 Alpha-Trade Pro: Full Trading Agent")

# 1. Assets Configuration
ticker_map = {
    "Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD", "RNDR (AI)": "RNDR-USD"
}

# 2. Sidebar Setup
asset_name = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])
st.sidebar.markdown("---")
inv = st.sidebar.number_input("Investment ($)", value=1000.0)

# 3. Data Loading
@st.cache_data
def get_market_data(ticker, interval):
    df = yf.download(ticker, period="1y", interval=interval)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = get_market_data(ticker_map[asset_name], tf)

if not data.empty:
    # Indicators
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)

    # UI Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"{asset_name} Price Chart")
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], name="SMA 50", line=dict(color='yellow')))
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Portfolio & Indicators")
        st.metric("Portfolio Value", f"${(inv * data['Close'].iloc[-1] / data['Open'].iloc[0]):,.2f}")
        st.write(f"**Current RSI:** {data['RSI'].iloc[-1]:.2f}")
        
        # AI Prediction
        st.subheader("🤖 AI Prediction")
        df_ai = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
        if df_ai['ds'].dt.tz is not None: df_ai['ds'] = df_ai['ds'].dt.tz_localize(None)
        model = Prophet(daily_seasonality=True)
        model.fit(df_ai)
        forecast = model.predict(model.make_future_dataframe(periods=30))
        st.line_chart(forecast.set_index('ds')['yhat'].tail(30))

    # Market Overview
    st.subheader("Global Top Market Data")
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
        market_data = pd.DataFrame(requests.get(url).json())
        AgGrid(market_data[['name', 'symbol', 'current_price', 'market_cap_change_percentage_24h']])
    except:
        st.error("Market data currently unavailable.")

else:
    st.error("Data not found. Please try again.")
