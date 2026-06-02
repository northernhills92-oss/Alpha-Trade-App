import streamlit as st
import plotly.graph_objects as go

from core.data_loader import load_data
from core.indicators import add_indicators
from ai.consensus import consensus_signal
from core.backtester import run_backtest
from whale.whale_tracker import detect_whale_activity
from sentiment.fear_greed import get_fear_greed
from core.journal import log_trade


st.set_page_config(
    page_title="Alpha Trade AI",
    layout="wide"
)

st.title("🚀 Alpha Trade AI Ultra")

asset = st.selectbox(
    "Asset",
    ["BTC-USD", "ETH-USD"]
)


df = load_data(asset)

df = add_indicators(df)
st.write(df['Date'].dtype)
st.write(df['Date'].head())
signal = consensus_signal(df)

fear_greed = get_fear_greed()

whale = detect_whale_activity()

current_price = df['Close'].iloc[-1]

log_trade(
    asset,
    signal,
    current_price
)


col1, col2 = st.columns([3, 1])

with col1:

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['EMA20'],
            name="EMA20"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['EMA50'],
            name="EMA50"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    st.metric(
        "Current Signal",
        signal
    )

    st.metric(
        "Fear & Greed",
        fear_greed
    )

    st.metric(
        "Whale Status",
        whale
    )

    st.metric(
        "Current Price",
        f"${current_price:.2f}"
    )


backtest = run_backtest(df)

st.subheader("📊 Backtest")

st.write(backtest)
