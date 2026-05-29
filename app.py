import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Alpha-Trade", layout="wide")

# Telegram function
def send_telegram_message(message):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)
    except Exception as e:
        st.error(f"Error: {e}")

st.title("Alpha-Trade: Top 100 Crypto Market")

# Telegram Test Button
if st.button('Test Telegram Alert'):
    send_telegram_message("Alpha-Trade Pro: စနစ် အလုပ်လုပ်နေပါပြီ!")
    st.write("Alert ပို့လိုက်ပါပြီ!")

# Data Fetching
def get_top_100():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        st.error("API error!")
        return None

df = get_top_100()

if df is not None:
    # Column နာမည်တွေကို အရင်ဆုံး စစ်ဆေးပေးပါမယ်
    # အကယ်၍ Error ထပ်တက်ရင် st.write(df.columns) ကို သုံးပြီး အမှန်ကိုရှာပါ
    try:
        st.dataframe(df[['market_cap_rank', 'name', 'current_price', 'market_cap']], use_container_width=True)
    except KeyError:
        st.write("Column နာမည် မှားနေသည်။ အောက်ပါ Column များကို သုံးနိုင်သည်:")
        st.write(df.columns.tolist())
