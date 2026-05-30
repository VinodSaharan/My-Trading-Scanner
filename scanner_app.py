import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Stable Engine")

# Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_stocks(symbols):
    results = []
    # प्रोग्रेस बार जो दिखाई देगा कि कितना काम हुआ
    progress_bar = st.progress(0)
    
    for idx, symbol in enumerate(symbols):
        try:
            # 1. 10 सेकंड का टाइमआउट (अगर Yahoo नहीं जवाब दे रहा तो रुकना नहीं है)
            hist = yf.download(symbol, period="5d", interval="15m", progress=False, timeout=10)
            
            if hist.empty or len(hist) < 20: continue
            
            # 2. इंडिकेटर्स कैलकुलेशन
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            hist['RSI'] = get_rsi(hist['Close'])
            
            c1, c2, c3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
            
            # 3. स्ट्रेटेजी लॉजिक
            is_morning_star = (c1['Close'] < c1['Open']) and (c3['Close'] > c3['Open']) and (c3['Volume'] > c2['Volume'])
            is_near_vwap = abs(c3['Close'] - c3['VWAP']) < (c3['Close'] * 0.005)
            
            if is_morning_star and is_near_vwap:
                results.append({'Stock': symbol, 'Price': f"{c3['Close']:.2f}", 'SL': f"{c2['Low']:.2f}"})
            
            # प्रोग्रेस अपडेट
            progress_bar.progress((idx + 1) / len(symbols))
            
        except Exception as e:
            continue
    return results

if st.button("🚀 सुरक्षित स्कैन शुरू करें"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        
        st.write(f"कुल {len(all_symbols)} स्टॉक्स की जांच हो रही है...")
        data = scan_stocks(all_symbols)
        
        if data:
            st.dataframe(pd.DataFrame(data))
        else:
            st.warning("कोई सेटअप नहीं मिला।")
    except Exception as e:
        st.error(f"शीट पढ़ने में दिक्कत: {e}")
