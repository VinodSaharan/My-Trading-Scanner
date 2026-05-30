import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Test Code: Direct List")

# शीट लिंक के बजाय सीधे लिस्ट का उपयोग करें
all_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'SBIN.NS']

if st.button("🚀 सीधे लिस्ट चेक करें"):
    results = []
    for symbol in all_symbols:
        hist = yf.download(symbol, period="1d", interval="15m", progress=False)
        if not hist.empty:
            last_price = hist['Close'].iloc[-1]
            results.append({'Stock': symbol, 'Price': f"{float(last_price):.2f}"})
    
    st.table(pd.DataFrame(results))
