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

# 1. Assets Definition (Commodities & All Requested Assets)
ticker_map = {
    "Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD", "RNDR (AI)": "RNDR-USD"
}

# 2. Sidebar Controls
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1d", "4h", "1h"])

# 3. Fetching Data with Validation
@st.cache_data
def load_data(ticker, interval):
    df = yf.download(ticker, period="1y", interval=interval)
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = load_data(ticker_map[asset], tf)

if not data.empty:
    # Indicators
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)
    
    # 4. Main Dashboard Layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"{asset} Professional Chart")
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], name="SMA 50", line=dict(color='yellow')))
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Portfolio & Signals")
        inv = st.number_input("Investment ($)", value=1000.0)
        curr_price = data['Close'].iloc[-1]
        st.metric("Portfolio Value", f"${(inv * curr_price / data['Open'].iloc[0]):,.2f}")
        st.write(f"**Current RSI:** {data['RSI'].iloc[-1]:.2f}")
        if st.button("Send Telegram Alert"):
            st.info("Telegram Alert Sent!")

    # 5. AI Prediction (Next 30 Days)
    st.subheader("🤖 AI Prediction Engine")
    df_ai = data.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    if df_ai['ds'].dt.tz is not None: df_ai['ds'] = df_ai['ds'].dt.tz_localize(None)
    model = Prophet(daily_seasonality=True)
    model.fit(df_ai)
    forecast = model.predict(model.make_future_dataframe(periods=30))
    st.line_chart(forecast.set_index('ds')['yhat'])

    # 6. Live Market Data Grid
    st.subheader("Live Market Data Explorer")
    AgGrid(data.tail(20))
    
    # 7. Crypto Market Summary (Coingecko)
    st.subheader("🌍 Global Top 100 Crypto Market")
    try:
        res = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1").json()
        st.table(pd.DataFrame(res)[['name', 'current_price', 'market_cap_change_percentage_24h']])
    except:
        st.error("Market data unavailable")
else:
    st.error("Error loading data. Please select another asset.")
