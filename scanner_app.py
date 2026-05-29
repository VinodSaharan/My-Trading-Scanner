import streamlit as st
import yfinance as yf
import pandas as pd

# 1. पेज सेटअप
st.set_page_config(page_title="प्रो स्टॉक स्कैनर", page_icon="📈", layout="wide")

# 2. स्टाइलिश CSS
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; background-color: #2E86C1; color: white; font-weight: bold;}
    h1 {color: #2E86C1; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 प्रो स्टॉक स्कैनर")

# 3. डेटा लोडिंग
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

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
            
            # कंडीशन
            if current_price > sma50 and change > 2.0 and volume > data['Volume'][symbol].iloc[-2]:
                results.append({
                    'Stock': symbol, 
                    'Price': float(current_price), 
                    'Change %': float(change),
                    'SMA50': float(sma50)
                })
            
            progress_bar.progress((i + 1) / len(symbols))
        except:
            continue
    
    # 5. रिजल्ट डिस्प्ले
    if results:
        res_df = pd.DataFrame(results).sort_values(by='Change %', ascending=False).head(20)
        st.success(f"कुल {len(results)} में से टॉप 20 स्टॉक्स मिल गए!")
        
        # साफ़-सुथरी और फॉर्मेट की हुई टेबल
        st.dataframe(
            res_df,
            column_config={
                "Change %": st.column_config.NumberColumn("Change %", format="%.2f%%"),
                "Price": st.column_config.NumberColumn("Price", format="%.2f"),
                "SMA50": st.column_config.NumberColumn("SMA50", format="%.2f"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Excel डाउनलोड
        st.download_button("📥 Excel में डाउनलोड करें", res_df.to_csv(index=False), "top_stocks.csv")
    else:
        st.warning("आज कोई भी स्टॉक इन शर्तों पर मैच नहीं हुआ।")
