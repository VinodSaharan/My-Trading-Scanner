import streamlit as st
import yfinance as yf
import pandas as pd

# 1. पेज सेटअप
st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Master Terminal")

# 2. यहाँ अपनी Google Sheet का CSV लिंक डालें (जो आपने पब्लिश किया है)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv" 

@st.cache_data(ttl=600)
def get_symbols():
    try:
        df = pd.read_csv(SHEET_URL)
        return df['Symbol'].tolist()
    except:
        return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS'] # Default List

def get_data(symbol):
    df = yf.download(symbol, period="5d", interval="15m", progress=False)
    df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

# 3. मुख्य लॉजिक
if st.button("🚀 लाइव स्कैन शुरू करें"):
    symbols = get_symbols()
    results = []
    
    with st.spinner('डेटा एनालाइज हो रहा है...'):
        for symbol in symbols:
            try:
                df = get_data(symbol)
                curr, prev = df.iloc[-1], df.iloc[-2]
                
                signal = "⚪ WAIT"
                if prev['EMA9'] <= prev['EMA21'] and curr['EMA9'] > curr['EMA21']: signal = "🟢 BUY"
                elif prev['EMA9'] >= prev['EMA21'] and curr['EMA9'] < curr['EMA21']: signal = "🔴 SELL"
                
                results.append({'Stock': symbol, 'Signal': signal, 'Price': round(float(curr['Close']), 2), 'RSI': round(float(curr['RSI']), 2)})
            except: continue
        
        # 4. कलर टेबल
        res_df = pd.DataFrame(results)
        def style_table(val):
            color = 'green' if val == '🟢 BUY' else 'red' if val == '🔴 SELL' else 'white'
            return f'color: {color}; font-weight: bold'

        st.dataframe(res_df.style.map(style_table, subset=['Signal']), use_container_width=True)

st.sidebar.info("Intrabullscanner22 v1.0")
