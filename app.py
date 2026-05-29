import streamlit as st
import pandas as pd
import yfinance as yf # Commodities အတွက်

st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")

st.title("Alpha-Trade Pro: Commodities & Crypto AI")

# Commodities Assets များ
assets = {
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
    "Silver": "SI=F",
    "Platinum": "PL=F"
}

def get_commodity_data(ticker):
    data = yf.Ticker(ticker).history(period="1d")
    return data['Close'].iloc[-1]

# Dashboard ပြသခြင်း
col1, col2, col3, col4 = st.columns(4)
cols = [col1, col2, col3, col4]

for i, (name, ticker) in enumerate(assets.items()):
    price = get_commodity_data(ticker)
    cols[i].metric(label=name, value=f"${price:,.2f}")

st.write("---")
st.subheader("Market Analysis (Commodities)")
# ဒီနေရာမှာ အစ်ကို့ရဲ့ Fibonacci/RSI Logic တွေကို Asset တစ်ခုချင်းစီအတွက် ထပ်ထည့်နိုင်ပါပြီ!
