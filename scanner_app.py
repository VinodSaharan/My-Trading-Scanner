import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Master Scanner", layout="wide")
st.title("🚀 Master RSI + VWAP Scanner")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def get_rsi(hist, period=14):
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 1. डेटा को रंगीन बनाने के लिए स्टाइलिंग फंक्शन
def color_signals(val):
    if 'BUY' in val: return 'background-color: #006400; color: white' # Dark Green
    if 'SELL' in val: return 'background-color: #8B0000; color: white' # Dark Red
    return ''

if st.button("🚀 स्कैन शुरू करें"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        results = []
        
        for symbol in all_symbols:
            try:
                hist = yf.download(symbol, period="2d", interval="15m", progress=False, timeout=5)
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                
                # VWAP & RSI
                tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
                hist['VWAP'] = (tp * hist['Volume']).cumsum() / hist['Volume'].cumsum()
                hist['RSI'] = get_rsi(hist)
                
                # % Change (आज की क्लोजिंग बनाम कल की क्लोजिंग)
                pct_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                
                # लॉजिक
                last = hist.iloc[-1]
                signal = ""
                if last['RSI'] < 30 and last['Close'] > last['VWAP']: signal = '🟢 BUY (Bullish)'
                elif last['RSI'] > 70 and last['Close'] < last['VWAP']: signal = '🔴 SELL (Bearish)'
                
                if signal:
                    results.append({
                        'Stock': symbol, 'Price': f"{last['Close']:.2f}", 
                        'RSI': f"{last['RSI']:.1f}", 'Change %': f"{pct_change:.2f}%", 'Signal': signal
                    })
            except: continue
        
        if results:
            df = pd.DataFrame(results)
            # 2. स्टाइलिंग लागू करें
            st.dataframe(df.style.applymap(color_signals, subset=['Signal']), use_container_width=True)
        else:
            st.info("अभी कोई ट्रेड सेटअप नहीं मिला।")
    except Exception as e:
        st.error(f"एरर: {e}")
