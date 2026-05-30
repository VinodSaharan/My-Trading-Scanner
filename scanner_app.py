import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="VWAP + ST Scanner", layout="wide")
st.title("🚀 VWAP + SuperTrend | Batch Scanner (25 Stocks/Batch)")

# अपनी Google Sheet का URL यहाँ डालें
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def get_supertrend(hist, period=10, multiplier=3):
    hl2 = (hist['High'] + hist['Low']) / 2
    atr = hist['High'].rolling(period).max() - hist['Low'].rolling(period).min()
    hist['Upper'] = hl2 + (multiplier * atr)
    return hist

def scan_batch(symbols):
    results = []
    for symbol in symbols:
        try:
            # 5-सेकंड टाइमआउट के साथ डेटा डाउनलोड
            hist = yf.download(symbol, period="2d", interval="15m", progress=False, timeout=5)
            if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
            if len(hist) < 20: continue
            
            # VWAP Calculation
            tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (tp * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            
            # SuperTrend Calculation
            hist = get_supertrend(hist)
            
            # Entry Logic: प्राइस VWAP और SuperTrend दोनों के ऊपर होनी चाहिए
            last = hist.iloc[-1]
            if last['Close'] > last['VWAP'] and last['Close'] > last['Upper']:
                results.append({
                    'Stock': symbol, 
                    'Price': f"{last['Close']:.2f}", 
                    'Signal': 'BULLISH'
                })
        except: continue
    return results

if st.button("🚀 25-25 के बैच में स्कैन शुरू करें"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        
        chunk_size = 25
        for i in range(0, len(all_symbols), chunk_size):
            batch = all_symbols[i:i + chunk_size]
            st.write(f"🔄 **बैच {i//chunk_size + 1} स्कैन हो रहा है...**")
            
            data = scan_batch(batch)
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            
            # Yahoo सर्वर के लिए ब्रेक
            time.sleep(2) 
            
    except Exception as e:
        st.error(f"शीट में गड़बड़ है: {e}")
