import streamlit as st
import yfinance as yf
import pandas as pd

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"
df = pd.read_csv(url)
# यहाँ अपने कॉलम का नाम पक्का रखें
symbols = df['Symbol'].tolist() 

st.title("मेरा स्टॉक स्कैनर 📈")

if st.button("स्कैन करें"):
    # एक साथ डाउनलोड करें
    data = yf.download(symbols, period="2d", group_by='ticker', threads=True)
    
    results = []
    
    for symbol in symbols:
        # अगर डेटा मिल गया है
        if symbol in data.columns.levels[0]:
            hist = data[symbol]
            # यह पक्का करें कि डेटा में कम से कम 2 दिन का क्लोजिंग प्राइस है
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                
                if current_price > prev_close:
                    change = ((current_price - prev_close) / prev_close) * 100
                    results.append({'Stock': symbol, 'Price': round(current_price, 2), 'Change %': round(change, 2)})
    
    if results:
        res_df = pd.DataFrame(results)
        st.table(res_df)
    else:
        st.warning("कोई भी स्टॉक आज 'Green' में नहीं है, या डेटा डाउनलोड नहीं हुआ।")
        st.write("डेटा प्रीव्यू:", data.head()) # यह चेक करने के लिए कि डेटा कैसा आ रहा है
