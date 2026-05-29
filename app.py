import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import ta
import requests

st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")
st.title("Alpha-Trade Pro: Final Trading Agent")

# 1. Assets Configuration
ticker_map = {
    "Gold": "GC=F", "Oil": "CL=F", "Silver": "SI=F", "Platinum": "PL=F",
    "BTC": "BTC-USD", "ETH": "ETH-USD", "FET (AI)": "FET-USD", "RNDR (AI)": "RNDR-USD"
}

# 2. Sidebar Controls
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))
tf = st.sidebar.selectbox("Timeframe", ["1mo", "1wk", "1d", "4h", "1h"])

# 3. Data Fetching & Error Handling
data = yf.download(ticker_map[asset], period="1y", interval=tf)
if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 4. Technical Indicators
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    data['SMA'] = ta.trend.sma_indicator(data['Close'], window=50)

    # 5. Auto Support & Resistance (Pivot points logic)
    pivot = (data['High'].iloc[-2] + data['Low'].iloc[-2] + data['Close'].iloc[-2]) / 3
    support = (pivot * 2) - data['High'].iloc[-2]
    resistance = (pivot * 2) - data['Low'].iloc[-2]

    # 6. Candlestick Chart with Indicators
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], name="SMA 50", line=dict(color='yellow', width=1)))
    fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="Support")
    fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="Resistance")
    fig.update_layout(title=f"{asset} Analysis", xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 7. Signals & Telegram Alert
    rsi_val = data['RSI'].iloc[-1]
    st.write(f"### Current RSI: {rsi_val:.2f}")
    
    msg = f"Alert: {asset} is at {data['Close'].iloc[-1]:.2f} | RSI: {rsi_val:.2f}"
    if rsi_val < 30:
        st.success(f"Buy Signal! {msg}")
    
    if st.button("Send Telegram Alert"):
        try:
            token = st.secrets["TELEGRAM_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}")
            st.success("Alert sent to Telegram!")
        except:
            st.error("Telegram Secrets not configured.")

# 8. Top Market Overview
st.subheader("Live Market Overview")
crypto_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
try:
    market_df = pd.DataFrame(requests.get(crypto_url).json())
    st.table(market_df[['name', 'current_price', 'market_cap_change_percentage_24h']])
except:
    st.write("Market data currently unavailable.")
