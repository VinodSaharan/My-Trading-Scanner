import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="प्रो स्टॉक स्कैनर", page_icon="📈")
st.title("📈 प्रो स्टॉक स्कैनर (Trend Filter)")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df['Symbol'].dropna().tolist()

symbols = load_data(url)

if st.button("🚀 ट्रेंड स्कैन करें"):
    with st.spinner('डेटा का विश्लेषण (Analysis) किया जा रहा है...'):
        # 60 दिन का डेटा लें ताकि 50-दिन का औसत (SMA) निकाल सकें
        data = yf.download(symbols, period="60d", group_by='column', threads=True)
        
        results = []
        
        for symbol in symbols:
            try:
                # क्लोजिंग प्राइस और 50-दिन का SMA
                close_prices = data['Close'][symbol]
                current_price = close_prices.iloc[-1]
                sma50 = close_prices.iloc[-50:].mean() # पिछले 50 दिनों का औसत
                
                # कंडीशन: प्राइस आज बढ़ा हो AND प्राइस 50-दिन के SMA से ऊपर हो
                if current_price > close_prices.iloc[-2] and current_price > sma50:
                    change = ((current_price - close_prices.iloc[-2]) / close_prices.iloc[-2]) * 100
                    results.append({
                        'Stock': symbol, 
                        'Price': round(float(current_price), 2), 
                        'Change %': round(float(change), 2),
                        'SMA50': round(float(sma50), 2)
                    })
            except Exception:
                continue
        
        if results:
            st.success(f"कुल {len(results)} स्टॉक्स 'बढ़त' और 'मजबूत ट्रेंड' में हैं!")
            res_df = pd.DataFrame(results)
            st.table(res_df.sort_values(by='Change %', ascending=False))
        else:
            st.warning("आज कोई भी स्टॉक इस कंडीशन पर मैच नहीं हुआ।")
