import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 Price Checker (Fixed)")

# टेस्ट के लिए लिस्ट
all_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'SBIN.NS']

if st.button("🚀 प्राइस चेक करें"):
    results = []
    
    # लूप यहाँ से शुरू होता है
    for symbol in all_symbols:
        try:
            hist = yf.download(symbol, period="1d", interval="15m", progress=False, timeout=5)
            
            # मल्टी-इंडेक्स फिक्स
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            if hist.empty:
                continue # यह 'continue' लूप के अंदर है, अब यह सही काम करेगा
                
            last_price = hist['Close'].iloc[-1]
            
            # अगर last_price एक सीरीज है तो उसका पहला मान लें
            if isinstance(last_price, pd.Series):
                last_price = last_price.iloc[0]
            
            results.append({'Stock': symbol, 'Price': f"{float(last_price):.2f}"})
            
        except Exception as e:
            st.write(f"Error on {symbol}: {e}")
            continue # यह भी लूप के अंदर है
            
    # लूप के बाहर रिजल्ट दिखाएं
    if results:
        st.dataframe(pd.DataFrame(results))
    else:
        st.error("डेटा नहीं मिला।")
