import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="VWAP Scanner", layout="wide")
st.title("📈 VWAP Crossover Scanner")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def scan_stocks(symbols):
    results = []
    for symbol in symbols:
        try:
            # डेटा डाउनलोड
            hist = yf.download(symbol, period="2d", interval="15m", progress=False)
            
            # मल्टी-कॉलम एरर को फिक्स करने के लिए:
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)
            
            if len(hist) < 2: continue
            
            # VWAP कैलकुलेशन (अब यह मल्टी-इंडेक्स से परेशान नहीं होगा)
            tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
            volume = hist['Volume']
            hist['VWAP'] = (tp * volume).cumsum() / volume.cumsum()
            
            # Crossover लॉजिक
            prev_close = hist['Close'].iloc[-2]
            prev_vwap = hist['VWAP'].iloc[-2]
            curr_close = hist['Close'].iloc[-1]
            curr_vwap = hist['VWAP'].iloc[-1]
            
            if prev_close < prev_vwap and curr_close > curr_vwap:
                results.append({'Stock': symbol, 'Price': f"{float(curr_close):.2f}", 'Signal': 'VWAP Breakout'})
        except Exception as e:
            continue
    return results

if st.button("🚀 स्कैन शुरू करें"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        data = scan_stocks(all_symbols)
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.warning("अभी कोई ब्रेकआउट नहीं मिला।")
    except Exception as e:
        st.error(f"शीट पढ़ने में दिक्कत: {e}")
