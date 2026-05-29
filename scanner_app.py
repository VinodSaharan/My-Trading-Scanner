import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Stable Scanner")

# अपनी शीट का लिंक यहाँ रखें
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_stocks(symbols):
    results = []
    for symbol in symbols:
        # सिंबल को क्लीन करें (सिर्फ एक बार .NS)
        clean_symbol = symbol.replace('.NS', '').strip() + '.NS'
        
        try:
            # सर्वर लोड बचाने के लिए छोटा पॉज़
            time.sleep(1.5) 
            
            hist = yf.download(clean_symbol, period="5d", interval="15m", progress=False)
            if len(hist) < 20: continue
            
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            hist['RSI'] = get_rsi(hist['Close'])
            
            c1, c2, c3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
            
            # मॉर्निंग स्टार + कंडीशन
            is_morning_star = (c1['Close'] < c1['Open']) and (c3['Close'] > c3['Open']) and (c3['Volume'] > c2['Volume'])
            is_near_vwap = abs(c3['Close'] - c3['VWAP']) < (c3['Close'] * 0.005)
            
            if is_morning_star and is_near_vwap:
                price = float(c3['Close'].squeeze())
                stop_loss = float(c2['Low'].squeeze())
                target = price + ((price - stop_loss) * 2)
                
                results.append({
                    'Stock': clean_symbol, 
                    'Signal': '🟢 BUY', 
                    'Price': f"{price:.2f}",
                    'SL': f"{stop_loss:.2f}",
                    'Target': f"{target:.2f}"
                })
        except: 
            continue
    return results

symbols_df = pd.read_csv(SHEET_URL, header=None)
symbols = symbols_df.iloc[:, 0].dropna().tolist()

if st.button("🚀 सुरक्षित स्कैन शुरू करें"):
    with st.spinner('डेटा फेच हो रहा है... कृपया प्रतीक्षा करें (पॉज़ के साथ):'):
        data = scan_stocks(symbols)
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.warning("कोई सेटअप नहीं मिला। बाजार में अभी शांति है।")
