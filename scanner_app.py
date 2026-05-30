import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Batch Scan Mode")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

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
            # हर स्टॉक के लिए छोटा ब्रेक ताकि Yahoo ब्लॉक न करे
            time.sleep(5.0) 
            hist = yf.download(symbol, period="5d", interval="15m", progress=False)
            
            if hist.empty or len(hist) < 20: continue
            
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            hist['RSI'] = get_rsi(hist['Close'])
            
            c1, c2, c3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
            
            if (c1['Close'] < c1['Open']) and (c3['Close'] > c3['Open']) and (c3['Volume'] > c2['Volume']):
                if abs(c3['Close'] - c3['VWAP']) < (c3['Close'] * 0.005):
                    if 40 < float(c3['RSI']) < 70:
                        results.append({
                            'Stock': symbol, 'Price': f"{float(c3['Close']):.2f}",
                            'SL': f"{float(c2['Low']):.2f}"
                        })
        except: continue
    return results

if st.button("🚀 सुरक्षित बैच स्कैन शुरू करें"):
    symbols_df = pd.read_csv(SHEET_URL, header=None)
    all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
    
    # 25-25 के ग्रुप में बांटना
    chunk_size = 25
    for i in range(0, len(all_symbols), chunk_size):
        chunk = all_symbols[i:i + chunk_size]
        st.write(f"🔄 बैच {i//chunk_size + 1} स्कैन हो रहा है ({len(chunk)} स्टॉक्स)...")
        
        batch_results = scan_batch(chunk)
        if batch_results:
            st.dataframe(pd.DataFrame(batch_results), use_container_width=True)
        else:
            st.info(f"बैच {i//chunk_size + 1} में कोई सेटअप नहीं मिला।")
        
        # हर बैच के बाद बड़ा ब्रेक ताकि सर्वर पूरी तरह रिफ्रेश हो जाए
        time.sleep(5)
