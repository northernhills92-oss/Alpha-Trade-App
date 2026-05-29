import streamlit as st
import pandas as pd
import requests
import yfinance as yf

st.set_page_config(page_title="Alpha-Trade Pro", layout="wide")

st.title("Alpha-Trade Pro: Crypto & Commodities AI")

# --- Commodities Data ---
st.subheader("Commodities Market")
assets = {
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
    "Silver": "SI=F",
    "Platinum": "PL=F"
}

cols = st.columns(4)
for i, (name, ticker) in enumerate(assets.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        price = data['Close'].iloc[-1]
        cols[i].metric(label=name, value=f"${price:,.2f}")
    except:
        cols[i].write(f"{name}: Data Error")

st.divider()

# --- Crypto Data ---
st.subheader("Top Crypto Market")
url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
try:
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        # လိုချင်တဲ့ အချက်အလက်များကို ရွေးပြခြင်း
        st.dataframe(df[['name', 'current_price', 'market_cap', 'high_24h', 'low_24h']], use_container_width=True)
    else:
        st.error("Crypto API ခေတ္တအလုပ်မလုပ်ပါ")
except:
    st.error("Crypto Data ဆွဲယူရာတွင် အမှားဖြစ်နေပါသည်")
