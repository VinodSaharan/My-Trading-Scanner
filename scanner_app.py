import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Robust Version")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def scan_stocks(symbols):
    results = []
    for symbol in symbols:
        try:
            # 1.5 सेकंड का पॉज़ ताकि Rate Limit न हो
            time.sleep(1.5) 
            
            # डेटा डाउनलोड
            hist = yf.download(symbol, period="5d", interval="15m", progress=False)
            
            # अगर डेटा खाली है (Delisted या गलत सिंबल), तो सीधे अगले पर जाएं
            if hist.empty or len(hist) < 20:
                continue
                
            # कैलकुलेशन
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            
            # (आगे का वही लॉजिक...)
            # ... (Morning Star और अन्य कंडीशन यहाँ आएं)
            
        except Exception as e:
            # अगर कोई भी एरर आए (जैसे delist होना), तो इसे प्रिंट करें और चलते रहें
            continue
    return results
