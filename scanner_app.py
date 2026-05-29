import streamlit as st
import yfinance as yf
import pandas as pd

# 1. पेज सेटअप
st.set_page_config(page_title="प्रो स्टॉक स्कैनर", page_icon="📈", layout="wide")
st.title("🚀 प्रो स्टॉक स्कैनर (Top 20 Analysis)")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df['Symbol'].dropna().tolist()

symbols = load_data(url)

# 2. बटन और बड़ा स्पिनर
if st.button("🔥 टॉप 20 स्टॉक्स स्कैन करें"):
    # बड़ा स्पिनर दिखाने के लिए कंटेनर
    with st.container():
        with st.spinner('डेटा का गहन विश्लेषण किया जा रहा है...'):
            # डेटा डाउनलोड
            data = yf.download(symbols, period="60d", group_by='column', threads=True)
            
            results = []
            
            for symbol in symbols:
                try:
                    close_prices = data['Close'][symbol]
                    current_price = close_prices.iloc[-1]
                    prev_close = close_prices.iloc[-2]
                    sma50 = close_prices.iloc[-50:].mean()
                    volume = data['Volume'][symbol].iloc[-1]
                    
                    # नई और कठिन कंडीशंस:
                    # 1. प्राइस SMA50 के ऊपर हो
                    # 2. आज का उछाल 2% से ज्यादा हो
                    # 3. आज का वॉल्यूम पिछले दिन से ज्यादा हो (डिमांड बढ़ रही है)
                    change = ((current_price - prev_close) / prev_close) * 100
                    
                    if current_price > sma50 and change > 2.0 and volume > data['Volume'][symbol].iloc[-2]:
                        results.append({
                            'Stock': symbol, 
                            'Price': round(float(current_price), 2), 
                            'Change %': round(float(change), 2),
                            'SMA50': round(float(sma50), 2)
                        })
                except Exception:
                    continue
            
            # रिजल्ट को 'Change %' के हिसाब से सॉर्ट करें और Top 20 लें
            if results:
                res_df = pd.DataFrame(results).sort_values(by='Change %', ascending=False).head(20)
                st.success(f"कुल {len(results)} में से टॉप 20 स्टॉक्स यहाँ हैं:")
                st.table(res_df)
                
                # Excel डाउनलोड बटन
                csv = res_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Excel/CSV में डाउनलोड करें", csv, "top_stocks.csv", "text/csv")
            else:
                st.warning("आज कोई भी स्टॉक इन कड़ी शर्तों (SMA50, >2% gain, High Volume) पर मैच नहीं हुआ।")
