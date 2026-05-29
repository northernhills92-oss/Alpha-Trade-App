import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from prophet import Prophet # AI Prediction အတွက်

st.set_page_config(page_title="Alpha-Trade Pro AI", layout="wide")
st.title("🤖 Alpha-Trade Pro: AI Prediction Engine")

# Assets
ticker_map = {"BTC": "BTC-USD", "ETH": "ETH-USD", "Gold": "GC=F"}
asset = st.sidebar.selectbox("Select Asset", list(ticker_map.keys()))

# Data Fetching
data = yf.download(ticker_map[asset], period="1y", interval="1d")
data.reset_index(inplace=True)

# AI Model (Prophet)
df_train = data[['Date', 'Close']]
df_train.columns = ['ds', 'y']

model = Prophet()
model.fit(df_train)

# Future Prediction (5 days)
future = model.make_future_dataframe(periods=5)
forecast = model.predict(future)

# Visualization
st.subheader(f"{asset} Price Prediction (Next 5 Days)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Actual Price"))
fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="AI Prediction", line=dict(dash='dot')))
st.plotly_chart(fig, use_container_width=True)

st.write("### AI Insights:")
st.write(f"Based on the trends, the AI predicts the next price trend for {asset} based on historical patterns.")
