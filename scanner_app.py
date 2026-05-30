import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="VWAP + ST Scanner", layout="wide")
st.title("🚀 Debug-Enabled VWAP Scanner")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def scan_batch(symbols):
    results = []
    # एक खाली प्लेसहोल्डर ताकि हम लाइव स्टेटस दिखा सकें
    status_text = st.empty() 
    
    for symbol in symbols:
        try:
            status_text.text(f"अभी स्कैन हो रहा है: {symbol}...")
            
            # 5 सेकंड का हार्ड टाइमआउट
            hist = yf.download(symbol, period="2d", interval="15m", progress=False, timeout=5)
            
            if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
            if len(hist) < 20: continue
            
            # Logic
            tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (tp * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            
            # SuperTrend (Simplified)
            hl2 = (hist['High'] + hist['Low']) / 2
            atr = hist['High'].rolling(10).max() - hist['Low'].rolling(10).min()
            upper = hl2 + (3 * atr)
            
            last = hist.iloc[-1]
            if last['Close'] > last['VWAP'] and last['Close'] > upper.iloc[-1]:
                results.append({'Stock': symbol, 'Price': f"{last['Close']:.2f}", 'Signal': 'BULLISH'})
        
        except Exception:
            continue
    
    status_text.text("बैच पूरा हुआ!")
    return results

if st.button("🚀 स्कैन शुरू करें"):
    symbols_df = pd.read_csv(SHEET_URL, header=None)
    all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
    
    chunk_size = 25
    for i in range(0, len(all_symbols), chunk_size):
        batch = all_symbols[i:i + chunk_size]
        st.write(f"🔄 बैच {i//chunk_size + 1}...")
        data = scan_batch(batch)
        if data:
            st.dataframe(pd.DataFrame(data))
        time.sleep(1)
