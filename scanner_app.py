import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Professional Stock Scanner", layout="wide")
st.title("📈 प्रो स्टॉक स्कैनर (Sheet Connected)")

# यहाँ अपना 'Publish to Web' वाला CSV लिंक डालें
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

if st.button("🚀 शीट से पूरी लिस्ट स्कैन करें"):
    try:
        # 1. Google Sheet से डेटा पढ़ें
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        st.write(f"कुल {len(all_symbols)} स्टॉक्स मिल गए। स्कैनिंग शुरू...")

        results = []
        for symbol in all_symbols:
            try:
                # 2. डेटा डाउनलोड करें
                hist = yf.download(symbol, period="1d", interval="15m", progress=False, timeout=5)
                
                # मल्टी-इंडेक्स फिक्स
                if isinstance(hist.columns, pd.MultiIndex):
                    hist.columns = hist.columns.get_level_values(0)
                
                if not hist.empty:
                    last_price = hist['Close'].iloc[-1]
                    if isinstance(last_price, pd.Series):
                        last_price = last_price.iloc[0]
                    
                    results.append({'Stock': symbol, 'Price': f"{float(last_price):.2f}"})
            except Exception:
                continue
        
        # 3. रिजल्ट दिखाएं
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("कोई डेटा नहीं मिला। लिंक और सिंबल चेक करें।")
            
    except Exception as e:
        st.error(f"शीट में गड़बड़ है: {e}")
