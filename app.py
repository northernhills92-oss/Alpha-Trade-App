import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
from prophet import Prophet
from st_aggrid import AgGrid

st.set_page_config(page_title="Alpha-Trade Pro: Master Dashboard", layout="wide")
st.title(" Alpha-Trade Pro: Full Integrated Agent")

# 1. Assets & Sidebar
ticker_map = {"Gold": "GC=F", "Oil": "CL=F", "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD"}
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])

# 2. Data Fetching
data = yf.download(ticker_map[asset], period="1y", interval=tf)
data.reset_index(inplace=True)
if data['Date'].dt.tz is not None:
    data['Date'] = data['Date'].dt.tz_localize(None)

# 3. Technical Indicators
data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)

# 4. Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{asset} Candlestick Analysis")
    fig = go.Figure(data=[go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA'], name="SMA 50", line=dict(color='yellow')))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Portfolio Tracker")
    inv = st.number_input("Investment ($)", value=1000.0)
    val = (inv * data['Close'].iloc[-1]) / data['Open'].iloc[0]
    st.metric("Estimated Portfolio Value", f"${val:,.2f}")
    st.write(f"### Current RSI: {data['RSI'].iloc[-1]:.2f}")

# 5. AI Prediction Engine
st.subheader("AI Price Prediction (Next 30 Days)")
df_train = data[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
model = Prophet(daily_seasonality=True)
model.fit(df_train)
forecast = model.predict(model.make_future_dataframe(periods=30))

fig_ai = go.Figure()
fig_ai.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Actual"))
fig_ai.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="AI Forecast", line=dict(dash='dot')))
fig_ai.update_layout(template="plotly_dark")
st.plotly_chart(fig_ai, use_container_width=True)

# 6. Data Grid
st.subheader("Raw Market Data")
AgGrid(data.tail(10))
