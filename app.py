import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Alpha-Trade", layout="wide")
st.title("Alpha-Trade: Top 100 Crypto Market")

def get_top_100():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    response = requests.get(url)
    return pd.DataFrame(response.json())

df = get_top_100()
st.dataframe(df[['market_cap_rank', 'name', 'current_price', 'market_cap']], use_container_width=True)
