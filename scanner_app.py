import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Master Scanner (Caching Enabled)")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

# 1. Caching: डेटा को 1 घंटे तक सेव रखेगा (Rate Limit एरर को खत्म करेगा)
@st.cache_data(ttl=3600)
def fetch_data(symbol):
    return yf.download(symbol, period="5d", interval="15m", progress=False)

def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_batch(symbols):
    results = []
    for symbol in symbols:
        try:
            hist = fetch_data(symbol)
            if hist is None or hist.empty or len(hist) < 20: continue
            
            # इंडिकेटर्स
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            hist['RSI'] = get_rsi(hist['Close'])
            
            c1, c2, c3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
            
            # स्ट्रेटेजी कंडीशन
            is_morning_star = (c1['Close'] < c1['Open']) and (c3['Close'] > c3['Open']) and (c3['Volume'] > c2['Volume'])
            is_near_vwap = abs(c3['Close'] - c3['VWAP']) < (c3['Close'] * 0.005)
            is_rsi_valid = 40 < float(c3['RSI']) < 70
            
            if is_morning_star and is_near_vwap and is_rsi_valid:
                results.append({
                    'Stock': symbol, 
                    'Price': f"{float(c3['Close']):.2f}",
                    'SL': f"{float(c2['Low']):.2f}",
                    'Target': f"{float(c3['Close']) + (float(c3['Close'] - c2['Low']) * 2):.2f}"
                })
        except: continue
    return results

# UI: स्कैनिंग
if st.button("🚀 सुरक्षित स्कैन शुरू करें"):
    symbols_df = pd.read_csv(SHEET_URL, header=None)
    all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
    
    chunk_size = 10
    for i in range(0, len(all_symbols), chunk_size):
        batch = all_symbols[i:i + chunk_size]
        st.write(f"🔄 बैच {i//chunk_size + 1} स्कैन हो रहा है...")
        
        data = scan_batch(batch)
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        
        time.sleep(1) # हल्का ब्रेक
