import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Pro Scanner")

# अपनी Google Sheet का URL यहाँ डालें
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
        clean_symbol = str(symbol).strip()
        try:
            # सर्वर एरर (Rate Limit) से बचने के लिए पॉज़
            time.sleep(5) 
            hist = yf.download(clean_symbol, period="5d", interval="15m", progress=False)
            
            if hist.empty or len(hist) < 20: continue
            
            # इंडिकेटर्स कैलकुलेशन
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            hist['RSI'] = get_rsi(hist['Close'])
            
            c1, c2, c3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
            
            # 4 कंडीशंस (Morning Star, VWAP, Volume, RSI)
            is_morning_star = (c1['Close'] < c1['Open']) and (c3['Close'] > c3['Open']) and (c3['Volume'] > c2['Volume'])
            is_near_vwap = abs(c3['Close'] - c3['VWAP']) < (c3['Close'] * 0.005)
            is_rsi_valid = 40 < float(c3['RSI']) < 70
            
            if is_morning_star and is_near_vwap and is_rsi_valid:
                price = float(c3['Close'].squeeze())
                stop_loss = float(c2['Low'].squeeze())
                target = price + ((price - stop_loss) * 2) # 1:2 रिस्क-रिवॉर्ड
                
                results.append({
                    'Stock': clean_symbol, 'Price': f"{price:.2f}",
                    'SL': f"{stop_loss:.2f}", 'Target': f"{target:.2f}"
                })
        except: continue
    return results

if st.button("🚀 स्कैन शुरू करें"):
    symbols_df = pd.read_csv(SHEET_URL, header=None)
    symbols = symbols_df.iloc[:, 0].dropna().tolist()
    
    with st.spinner('प्रोफेशनल एनालिसिस चल रहा है...'):
        data = scan_stocks(symbols)
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.warning("कोई सेटअप नहीं मिला। सही अवसर का इंतज़ार करें।")
