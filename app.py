import streamlit as st
import requests

# Telegram သို့ စာပို့မည့် Function
def send_telegram_message(message):
    try:
        # Streamlit Secrets မှ ခေါ်ယူခြင်း
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)
    except Exception as e:
        st.error(f"Error: {e}")

# ခလုတ်ကို Dashboard ရဲ့ အပေါ်ဆုံးမှာ ထားခြင်း
if st.button('Test Telegram Alert'):
    send_telegram_message("Alpha-Trade Pro: Bot စနစ် အောင်မြင်စွာ ချိတ်ဆက်ပြီးပါပြီ!")
    st.write("Alert ပို့လိုက်ပါပြီ! အစ်ကို့ Telegram ကို စစ်ကြည့်ပါ။")

# အောက်မှာ အစ်ကို့ရဲ့ လက်ရှိ Code တွေကို ဆက်ထားလိုက်ပါ...
import pandas as pd
# ... ကျန်တဲ့ Code များ ...

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
