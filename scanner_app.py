import streamlit as st
import yfinance as yf
import pandas as pd

# 1. पेज सेटअप
st.set_page_config(page_title="Intrabullscanner22", layout="wide")

# CSS: बड़ा UI और फुल-विड्थ टेबल
st.markdown("""
    <style>
        .stButton>button {width: 100%; height: 80px; font-size: 24px; font-weight: bold; background-color: #2E86C1; color: white; border-radius: 10px;}
        [data-testid="stDataFrame"] {width: 100% !important;}
    </style>
""", unsafe_allow_html=True)

st.title("📈 Intrabullscanner22 | Pro Terminal")

# 2. Google Sheet लिंक यहाँ डालें
# ध्यान दें: लिंक के अंत में '/export?format=csv' लगा होना चाहिए
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=600)
def get_symbols():
    try:
        # शीट पढ़ें
        df = pd.read_csv(SHEET_URL)
        # पहली कॉलम को स्टॉक्स लिस्ट मानेंगे
        stocks = df.iloc[:, 0].dropna().astype(str).tolist()
        # .NS जोड़ें अगर नहीं है
        return [s if '.NS' in s else s + '.NS' for s in stocks]
    except Exception as e:
        st.error(f"शीट पढ़ने में एरर: {e}")
        return ['RELIANCE.NS', 'TCS.NS']

def get_data(symbol):
    df = yf.download(symbol, period="5d", interval="15m", progress=False)
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

# 3. स्कैनिंग लॉजिक
if st.button("🚀 लाइव स्कैन शुरू करें"):
    symbols = get_symbols()
    results = []
    
    with st.spinner('डेटा फेच हो रहा है...'):
        for symbol in symbols:
            try:
                df = get_data(symbol)
                if df.empty: continue
                curr, prev = df.iloc[-1], df.iloc[-2]
                
                signal = "⚪ WAIT"
                if prev['EMA9'] <= prev['EMA21'] and curr['EMA9'] > curr['EMA21']: signal = "🟢 BUY"
                elif prev['EMA9'] >= prev['EMA21'] and curr['EMA9'] < curr['EMA21']: signal = "🔴 SELL"
                
                results.append({'Stock': symbol, 'Signal': signal, 'Price': round(float(curr['Close']), 2), 'RSI': round(float(curr['RSI']), 2)})
            except: continue
        
        if results:
            res_df = pd.DataFrame(results)
            def style_table(val):
                color = 'green' if val == '🟢 BUY' else 'red' if val == '🔴 SELL' else 'black'
                return f'color: {color}; font-weight: bold; font-size: 18px;'
            
            st.dataframe(res_df.style.map(style_table, subset=['Signal']), use_container_width=True)
        else:
            st.warning("कोई डेटा नहीं मिला। चेक करें कि शीट में सही स्टॉक्स हैं।")
