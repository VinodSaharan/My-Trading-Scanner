import streamlit as st
import yfinance as yf
import pandas as pd

st.title("🔍 डेटा चेकर (Price Tester)")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

if st.button("🚀 सिर्फ प्राइस चेक करें"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        
        st.write(f"कुल {len(all_symbols)} स्टॉक्स की लिस्ट मिली।")
        
        results = []
        for symbol in all_symbols:
            try:
                # 1 दिन का डेटा डाउनलोड करें
                hist = yf.download(symbol, period="1d", interval="15m", progress=False, timeout=5)
                if not hist.empty:
                    last_price = hist['Close'].iloc[-1]
                    results.append({'Stock': symbol, 'Price': f"{float(last_price):.2f}"})
            except:
                continue
        
        if results:
            st.dataframe(pd.DataFrame(results))
        else:
            st.error("डेटा नहीं मिला! कृपया Google Sheet का लिंक चेक करें।")
            
    except Exception as e:
        st.error(f"एरर: {e}")
