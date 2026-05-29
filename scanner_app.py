import streamlit as st
import yfinance as yf
import pandas as pd

# 1. पेज सेटअप (Wide Layout)
st.set_page_config(page_title="प्रो स्टॉक स्कैनर", page_icon="📈", layout="wide")

# 2. कस्टमाइज़ेशन के लिए CSS
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; background-color: #2E86C1; color: white; font-weight: bold;}
    h1 {color: #2E86C1; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 प्रो स्टॉक स्कैनर")

# 3. डेटा लोडिंग
url = "YOUR_PUBLISHED_CSV_LINK"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df['Symbol'].dropna().tolist()

symbols = load_data(url)

# 4. स्कैन बटन
if st.button("🔥 टॉप 20 स्टॉक्स स्कैन करें"):
    progress_bar = st.progress(0)
    results = []
    
    # डेटा डाउनलोड
    data = yf.download(symbols, period="60d", group_by='column', threads=True)
    
    for i, symbol in enumerate(symbols):
        try:
            close_prices = data['Close'][symbol]
            current_price = close_prices.iloc[-1]
            prev_close = close_prices.iloc[-2]
            sma50 = close_prices.iloc[-50:].mean()
            volume = data['Volume'][symbol].iloc[-1]
            
            change = ((current_price - prev_close) / prev_close) * 100
            
            # कंडीशन: SMA के ऊपर + 2% से ज्यादा बढ़त + हाई वॉल्यूम
            if current_price > sma50 and change > 2.0 and volume > data['Volume'][symbol].iloc[-2]:
                results.append({
                    'Stock': symbol, 
                    'Price': round(float(current_price), 2), 
                    'Change %': round(float(change), 2),
                    'SMA50': round(float(sma50), 2)
                })
            
            progress_bar.progress((i + 1) / len(symbols))
        except:
            continue
    
    # 5. रिजल्ट और कलरफुल टेबल
    if results:
        res_df = pd.DataFrame(results).sort_values(by='Change %', ascending=False).head(20)
        st.success(f"कुल {len(results)} में से टॉप 20 स्टॉक्स मिल गए!")
        
        # इंटरैक्टिव और कलरफुल टेबल
        st.dataframe(
            res_df.style.map(lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else '', subset=['Change %']),
            use_container_width=True
        )
        
        # Excel डाउनलोड
        st.download_button("📥 Excel में डाउनलोड करें", res_df.to_csv(index=False), "top_stocks.csv")
    else:
        st.warning("आज कोई भी स्टॉक इन शर्तों पर मैच नहीं हुआ।")
