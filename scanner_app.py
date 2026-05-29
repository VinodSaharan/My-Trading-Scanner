import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Intrabullscanner22", layout="wide")

st.title("📈 Intrabullscanner22 | Pro Terminal")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=600)
def get_symbols():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        stocks = df.iloc[:, 0].dropna().astype(str).tolist()
        return [s.strip() if '.NS' in s else s.strip() + '.NS' for s in stocks]
    except:
        return ['RELIANCE.NS', 'TCS.NS']

def get_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        if df.empty or len(df) < 21: return None
        
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 0.0001))))
        return df.fillna(0)
    except:
        return None

if st.button("🚀 लाइव स्कैन शुरू करें"):
    symbols = get_symbols()
    results = []
    
    with st.spinner('डेटा एनालाइज हो रहा है...'):
        for symbol in symbols:
            df = get_data(symbol)
            if df is None: continue
            
            # .iloc[-1] का उपयोग करके पक्की वैल्यू निकालें
            c_close = float(df['Close'].iloc[-1])
            c_ema9 = float(df['EMA9'].iloc[-1])
            c_ema21 = float(df['EMA21'].iloc[-1])
            p_ema9 = float(df['EMA9'].iloc[-2])
            p_ema21 = float(df['EMA21'].iloc[-2])
            rsi_val = float(df['RSI'].iloc[-1])
            
            signal = "⚪ WAIT"
            if p_ema9 <= p_ema21 and c_ema9 > c_ema21: signal = "🟢 BUY"
            elif p_ema9 >= p_ema21 and c_ema9 < c_ema21: signal = "🔴 SELL"
            
            results.append({
                'Stock': symbol, 
                'Signal': signal, 
                'Price': round(c_close, 2), 
                'RSI': round(rsi_val, 2)
            })
        
        if results:
            res_df = pd.DataFrame(results)
            def style_table(val):
                color = 'green' if val == '🟢 BUY' else 'red' if val == '🔴 SELL' else 'black'
                return f'color: {color}; font-weight: bold; font-size: 18px;'
            
            st.dataframe(res_df.style.map(style_table, subset=['Signal']), use_container_width=True)
        else:
            st.warning("कोई डेटा नहीं मिला।")
