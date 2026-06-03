import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.data_loader import load_data
from core.indicators import add_indicators
from ai.consensus import consensus_signal
from core.backtester import run_backtest
from whale.whale_tracker import detect_whale_activity
from sentiment.fear_greed import get_fear_greed
from core.journal import log_trade


# ===================================
# PAGE CONFIG
# ===================================

st.set_page_config(
    page_title="Alpha Trade AI Ultra",
    layout="wide"
)

st.title("🚀 Alpha Trade AI Ultra")


# ===================================
# ASSET SELECT
# ===================================

asset = st.selectbox(
    "Asset",
    [
        "BTC-USD",
        "ETH-USD"
    ]
)


# ===================================
# LOAD DATA
# ===================================

try:

    df = load_data(asset)

    df["Date"] = pd.to_datetime(
        df["Date"],
        utc=True
    ).dt.tz_convert(None)

except Exception as e:

    st.error(f"Data Error: {e}")
    st.stop()


if df.empty:

    st.error("No market data loaded.")
    st.stop()


# ===================================
# INDICATORS
# ===================================

try:

    df = add_indicators(df)

except Exception as e:

    st.error(f"Indicator Error: {e}")
    st.stop()


# ===================================
# AI SIGNAL
# ===================================

try:

    signal = consensus_signal(df)
    signal = "HOLD"

except Exception as e:

    st.warning(f"Signal Error: {e}")

    signal = "HOLD"


# ===================================
# MARKET INFO
# ===================================

try:
    fear_greed = get_fear_greed()
except:
    fear_greed = "N/A"

try:
    whale = detect_whale_activity()
except:
    whale = "N/A"


current_price = float(df["Close"].iloc[-1])


# ===================================
# JOURNAL
# ===================================

try:

    log_trade(
        asset,
        signal,
        current_price
    )

except:
    pass


# ===================================
# DASHBOARD
# ===================================

col1, col2 = st.columns([3, 1])


# ===================================
# CHART
# ===================================

with col1:

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price"
        )
    )

    if "EMA20" in df.columns:

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df["EMA20"],
                name="EMA20"
            )
        )

    if "EMA50" in df.columns:

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df["EMA50"],
                name="EMA50"
            )
        )

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
    fig,
    width="stretch"
    )

# ===================================
# METRICS
# ===================================

with col2:

    st.metric(
        "Current Signal",
        signal
    )

    st.metric(
        "Current Price",
        f"${current_price:,.2f}"
    )

    st.metric(
        "Fear & Greed",
        fear_greed
    )

    st.metric(
        "Whale Status",
        whale
    )


# ===================================
# BACKTEST
# ===================================

st.subheader("📊 Strategy Backtest")

try:

    result = run_backtest(df)

    st.json(result)

except Exception as e:

    st.error(f"Backtest Error: {e}")


# ===================================
# RAW DATA
# ===================================

with st.expander("View Raw Data"):

    sst.dataframe(
    df.tail(100),
    width="stretch"
    )
