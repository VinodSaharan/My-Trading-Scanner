import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="VWAP Scanner", layout="wide")
st.title("📈 VWAP Crossover Scanner (Sheet Version)")

# अपनी Google Sheet का URL यहाँ पेस्ट करें
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=600) # डेटा को 10 मिनट तक कैश करेगा (Rate limit से बचने के लिए)
def get_data(symbol):
    try:
        return yf.download(symbol, period="2d", interval="15m", progress=False, timeout=5)
    except:
        return None

def scan_stocks(symbols):
    results = []
    for symbol in symbols:
        hist = get_data(symbol)
        if hist is None or len(hist) < 2: continue
        
        # VWAP कैलकुलेशन
        hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
        hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
        
        # Crossover लॉजिक
        prev_close = hist['Close'].iloc[-2]
        prev_vwap = hist['VWAP'].iloc[-2]
        curr_close = hist['Close'].iloc[-1]
        curr_vwap = hist['VWAP'].iloc[-1]
        
        if prev_close < prev_vwap and curr_close > curr_vwap:
            results.append({'Stock': symbol, 'Price': f"{float(curr_close):.2f}", 'Signal': 'VWAP Breakout'})
            
    return results

if st.button("🚀 Google Sheet से स्कैन शुरू करें"):
    try:
        # शीट से लिस्ट लोड करना
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        
        st.write(f"कुल {len(all_symbols)} स्टॉक्स की जांच हो रही है...")
        data = scan_stocks(all_symbols)
        
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.warning("अभी कोई ब्रेकआउट नहीं मिला।")
    except Exception as e:
        st.error(f"शीट लिंक में गड़बड़ है: {e}")
