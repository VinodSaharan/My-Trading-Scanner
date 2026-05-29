import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Pro Strategy + Risk Management")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=60)
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_stocks(symbols):
    results = []
    for symbol in symbols:
        try:
            hist = yf.download(symbol, period="5d", interval="15m", progress=False)
            if len(hist) < 20: continue
            
            # VWAP & Indicators
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            hist['RSI'] = get_rsi(hist['Close'])
            
            c1, c2, c3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
            
            # Conditions
            is_morning_star = (c1['Close'] < c1['Open']) and (c3['Close'] > c3['Open']) and (c3['Volume'] > c2['Volume'])
            is_near_vwap = abs(c3['Close'] - c3['VWAP']) < (c3['Close'] * 0.005)
            
            if is_morning_star and is_near_vwap:
                price = float(c3['Close'].squeeze())
                stop_loss = float(c2['Low'].squeeze()) # Morning Star की बीच वाली कैंडल का लो
                target = price + ((price - stop_loss) * 2) # 1:2 रिस्क-रिवॉर्ड
                
                results.append({
                    'Stock': symbol, 
                    'Signal': '🟢 BUY', 
                    'Price': f"{price:.2f}",
                    'Stop Loss': f"{stop_loss:.2f}",
                    'Target': f"{target:.2f}"
                })
        except: continue
    return results

symbols_df = pd.read_csv(SHEET_URL, header=None)
symbols = [str(s).strip() + '.NS' for s in symbols_df.iloc[:, 0].dropna().tolist()]

if st.button("🚀 रिस्क-मैनेजमेंट के साथ स्कैन करें"):
    data = scan_stocks(symbols)
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("फिलहाल कोई ट्रेड सेटअप नहीं मिला।")
