import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="प्रो स्टॉक स्कैनर", page_icon="📈", layout="wide")

# CSS का इस्तेमाल करके ऐप को और सुंदर बनाना
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; background-color: #4CAF50; color: white;}
    h1 {color: #2E86C1; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 प्रो स्टॉक स्कैनर")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df['Symbol'].dropna().tolist()

symbols = load_data(url)

if st.button("🔥 टॉप 20 स्टॉक्स स्कैन करें"):
    progress_bar = st.progress(0) # प्रोग्रेस बार की शुरुआत
    results = []
    
    # डेटा डाउनलोड और प्रोसेसिंग
    data = yf.download(symbols, period="60d", group_by='column', threads=True)
    
    for i, symbol in enumerate(symbols):
        try:
            close_prices = data['Close'][symbol]
            current_price = close_prices.iloc[-1]
            prev_close = close_prices.iloc[-2]
            sma50 = close_prices.iloc[-50:].mean()
            
            change = ((current_price - prev_close) / prev_close) * 100
            
            if current_price > sma50 and change > 2.0:
                results.append({'Stock': symbol, 'Price': round(float(current_price), 2), 'Change %': round(float(change), 2)})
            
            # प्रोग्रेस बार को अपडेट करना
            progress_bar.progress((i + 1) / len(symbols))
        except:
            continue
    
    if results:
        res_df = pd.DataFrame(results).sort_values(by='Change %', ascending=False).head(20)
        
        # कलरफुल टेबल (Pandas Styler का उपयोग करके)
        def color_positive_green(val):
            color = 'green' if val > 0 else 'red'
            return f'color: {color}'
            
        st.success(f"टॉप 20 स्टॉक्स मिल गए!")
        st.dataframe(res_df.style.applymap(color_positive_green, subset=['Change %']))
        
        # डाउनलोड बटन
        st.download_button("📥 Excel में डाउनलोड करें", res_df.to_csv(index=False), "top_stocks.csv")
    else:
        st.warning("आज कोई स्टॉक मैच नहीं हुआ।")
