import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Master Scanner")

def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_stocks(symbols):
    results = []
    for symbol in symbols:
        # केवल valid symbols को प्रोसेस करें
        clean_symbol = str(symbol).strip()
        try:
            time.sleep(0.5) # हल्का पॉज़
            hist = yf.download(clean_symbol, period="5d", interval="15m", progress=False)
            
            # अगर डेटा खाली है, तो इसे नज़रअंदाज़ करें
            if hist is None or hist.empty or len(hist) < 20:
                continue
            
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            hist['RSI'] = get_rsi(hist['Close'])
            
            c1, c2, c3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
            
            # मॉर्निंग स्टार कंडीशन
            is_morning_star = (c1['Close'] < c1['Open']) and (c3['Close'] > c3['Open']) and (c3['Volume'] > c2['Volume'])
            is_near_vwap = abs(c3['Close'] - c3['VWAP']) < (c3['Close'] * 0.005)
            
            if is_morning_star and is_near_vwap:
                results.append({
                    'Stock': clean_symbol, 'Price': f"{float(c3['Close']):.2f}",
                    'SL': f"{float(c2['Low']):.2f}"
                })
        except:
            continue # एरर आने पर अगला स्टॉक चेक करें
    return results

# UI
if st.button("🚀 स्कैन शुरू करें"):
    symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS'] # यहाँ अपनी लिस्ट जोड़ें
    data = scan_stocks(symbols)
    if data:
        st.dataframe(pd.DataFrame(data))
    else:
        st.warning("कोई वैलिड सेटअप नहीं मिला।")
