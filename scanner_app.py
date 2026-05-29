import streamlit as st
import yfinance as yf
import pandas as pd

# 1. अपनी Google Sheet का लिंक यहाँ डालें
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"
df = pd.read_csv(url)
symbols = df['Symbol'].tolist()  # यहाँ अपने कॉलम का नाम लिखें

st.title("मेरा आसान स्टॉक स्कैनर 📈")

if st.button("स्कैन करें"):
    # डेटा डाउनलोड करना
    data = yf.download(symbols, period="2d", group_by='ticker', threads=True)
    
    results = []
    
    for symbol in symbols:
        try:
            # पिछले दिन का क्लोजिंग और आज का लेटेस्ट प्राइस
            hist = data[symbol]
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            
            # कंडीशन: अगर आज का भाव कल से ज्यादा है
            if current_price > prev_close:
                change = ((current_price - prev_close) / prev_close) * 100
                results.append({'Stock': symbol, 'Price': current_price, 'Change %': change})
        except:
            continue
    
    # रिजल्ट दिखाना
    res_df = pd.DataFrame(results)
    st.write("आज ऊपर जाने वाले स्टॉक्स:", res_df)
