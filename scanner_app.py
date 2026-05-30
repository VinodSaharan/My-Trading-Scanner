import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚀 Master RSI + VWAP Scanner")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def get_rsi(hist, period=14):
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if st.button("🚀 स्कैन शुरू करें"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        
        results = []
        progress_text = st.empty()
        
        for i, symbol in enumerate(all_symbols):
            progress_text.text(f"स्कैनिंग: {symbol} ({i+1}/{len(all_symbols)})")
            try:
                hist = yf.download(symbol, period="2d", interval="15m", progress=False, timeout=5)
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                
                tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
                hist['VWAP'] = (tp * hist['Volume']).cumsum() / hist['Volume'].cumsum()
                hist['RSI'] = get_rsi(hist)
                
                pct_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                
                last = hist.iloc[-1]
                if last['RSI'] < 30 and last['Close'] > last['VWAP']:
                    results.append({'Stock': symbol, 'Price': f"{last['Close']:.2f}", 'RSI': f"{last['RSI']:.1f}", 'Change %': f"{pct_change:.2f}%", 'Signal': 'BUY'})
                elif last['RSI'] > 70 and last['Close'] < last['VWAP']:
                    results.append({'Stock': symbol, 'Price': f"{last['Close']:.2f}", 'RSI': f"{last['RSI']:.1f}", 'Change %': f"{pct_change:.2f}%", 'Signal': 'SELL'})
            except: continue
        
        progress_text.text("स्कैन पूरा हुआ!")
        
        if results:
            # यहाँ हम साधारण टेबल दिखा रहे हैं जो हर हाल में काम करेगी
            st.table(pd.DataFrame(results))
        else:
            st.warning("कोई ट्रेड सेटअप नहीं मिला।")
    except Exception as e:
        st.error(f"एरर: {e}")
