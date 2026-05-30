import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Pro Trader Scanner", layout="wide")
st.title("📈 प्रो-ट्रेडर कलर-कोडेड डैशबोर्ड")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def get_rsi(hist, period=14):
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def highlight_signals(val):
    if 'BUY' in val: return 'background-color: #006400; color: white'
    if 'SELL' in val: return 'background-color: #8B0000; color: white'
    return ''

if st.button("🔍 मार्केट स्कैन करें", type="primary"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        results = []
        
        status_text = st.empty()
        
        for i, symbol in enumerate(all_symbols):
            status_text.text(f"स्कैनिंग: {i+1}/{len(all_symbols)} - {symbol}")
            try:
                hist = yf.download(symbol, period="2d", interval="15m", progress=False, timeout=5)
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                
                tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
                hist['VWAP'] = (tp * hist['Volume']).cumsum() / hist['Volume'].cumsum()
                hist['RSI'] = get_rsi(hist)
                
                pct_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                last = hist.iloc[-1]
                rsi = last['RSI']
                
                # यहाँ हमने आपके बताए अनुसार इमोजी सेट किए हैं
                signal = ""
                if rsi < 20 and last['Close'] > last['VWAP']: signal = '⚡ STRONG BUY 🟢'
                elif rsi < 30: signal = '✅ BUY 🟢'
                elif rsi > 80 and last['Close'] < last['VWAP']: signal = '🔥 STRONG SELL 🔴'
                elif rsi > 70: signal = '❌ SELL 🔴'
                
                if signal:
                    results.append({'Stock': symbol, 'Price': f"{last['Close']:.2f}", 'RSI': f"{rsi:.1f}", 'Change %': f"{pct_change:.2f}%", 'Signal': signal})
            except: continue
        
        status_text.text("स्कैन पूरा हुआ!")
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df.style.applymap(highlight_signals, subset=['Signal']), use_container_width=True)
        else:
            st.info("अभी कोई ट्रेड सेटअप नहीं मिला।")
    except Exception as e:
        st.error(f"एरर: {e}")
