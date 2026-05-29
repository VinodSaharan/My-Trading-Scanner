import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

# 1. पेज सेटअप
st.set_page_config(layout="wide", page_title="Live Trading Scanner")
st.title("🎯 Professional Cloud Trading Scanner")

# 2. Google Sheet से डेटा लोड करना
@st.cache_data(ttl=600) # डेटा हर 10 मिनट में रिफ्रेश होगा
def get_stocks():
    # यहाँ अपना पब्लिश किया हुआ CSV लिंक पेस्ट करें
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?gid=0&single=true&output=csv"
    "यहाँ_अपना_Google_Sheet_का_पब्लिश_CSV_लिंक_डाले"
    try:
        df = pd.read_csv(url)
        return df['Symbol'].tolist()
    except:
        return []

# 3. साइडबार कंट्रोल्स
st.sidebar.header("Scanner Settings")
stocks = get_stocks()
st.sidebar.write(f"कुल {len(stocks)} स्टॉक्स लोडेड हैं।")

strategy_mode = st.sidebar.radio("Mode", ["सभी कंडीशंस साथ में (AND)", "कोई भी एक कंडीशन (OR)"])
use_st = st.sidebar.checkbox("SuperTrend", True)
use_vwap = st.sidebar.checkbox("Price > VWAP", True)
use_vol = st.sidebar.checkbox("High Volume", True)

# 4. स्कैनर लॉजिक
if st.sidebar.button("Run Scan"):
    if not stocks:
        st.error("स्टॉक्स लिस्ट खाली है। Google Sheet लिंक चेक करें!")
    else:
        results = []
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(stocks):
            try:
                # 15 मिनट का डेटा (इंट्राडे के लिए)
                df = yf.download(ticker, period="5d", interval="15m", progress=False)
                if df.empty: continue
                
                # इंडिकेटर्स कैलकुलेशन
                df.ta.supertrend(length=10, multiplier=3, append=True)
                df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
                
                c1 = (df['SUPERT_10_3.0'].iloc[-1] == 1) if use_st else False
                c2 = (df['Close'].iloc[-1] > df['VWAP'].iloc[-1]) if use_vwap else False
                c3 = (df['Volume'].iloc[-1] > df['Volume'].rolling(10).mean().iloc[-1]) if use_vol else False
                
                # लॉजिक
                match = (c1 and c2 and c3) if strategy_mode == "सभी कंडीशंस साथ में (AND)" else (c1 or c2 or c3)
                
                if match:
                    results.append({"Symbol": ticker, "ST": "✅" if c1 else "❌", "VWAP": "✅" if c2 else "❌", "VOL": "✅" if c3 else "❌"})
            except: continue
            progress_bar.progress((i + 1) / len(stocks))

        # 5. रिजल्ट दिखाना
        if results:
            st.success("स्कैनिंग पूरी हुई!")
            df_results = pd.DataFrame(results)
            st.table(df_results)
            st.download_button("रिजल्ट डाउनलोड करें", df_results.to_csv(), "results.csv", "text/csv")
        else:
            st.warning("कोई रिजल्ट नहीं मिला।")
