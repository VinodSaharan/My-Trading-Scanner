import streamlit as st
import yfinance as yf
import pandas as pd
import time # जरूरी लाइब्रेरी

st.set_page_config(page_title="Pro 1000 Scanner", layout="wide")
st.title("⚡ प्रो-1000 गोल्डन स्कैनर")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

def get_indicators(hist):
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    hist['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    tp = (hist['High'] + hist['Low'] + hist['Close']) / 3
    hist['VWAP'] = (tp * hist['Volume']).cumsum() / hist['Volume'].cumsum()
    hist['EMA_200'] = hist['Close'].ewm(span=200, adjust=False).mean()
    
    hist['BB_Mid'] = hist['Close'].rolling(window=20).mean()
    hist['BB_Std'] = hist['Close'].rolling(window=20).std()
    hist['BB_Upper'] = hist['BB_Mid'] + (hist['BB_Std'] * 2)
    hist['BB_Lower'] = hist['BB_Mid'] - (hist['BB_Std'] * 2)
    return hist

def make_clickable(symbol):
    clean_symbol = symbol.replace(".NS", "")
    url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_symbol}"
    return f'<a target="_blank" href="{url}" style="color: blue;">{clean_symbol}</a>'

if st.button("🔍 1000 स्टॉक्स स्कैन करें", type="primary"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        raw_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        all_symbols = [f"{s}.NS" if not s.endswith(".NS") else s for s in raw_symbols]
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(all_symbols):
            # प्रगति दिखाएं
            progress = (i + 1) / len(all_symbols)
            progress_bar.progress(progress)
            status_text.text(f"स्कैनिंग ({i+1}/{len(all_symbols)}): {symbol}")
            
            try:
                hist = yf.download(symbol, period="2y", interval="1d", progress=False, timeout=5, auto_adjust=True)
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                hist = get_indicators(hist)
                
                last = hist.iloc[-1]
                
                # गोल्डन कॉम्बो लॉजिक
                if (last['RSI'] < 30) and (last['Close'] > last['EMA_200']) and (last['Close'] <= last['BB_Lower']):
                    results.append({'Stock': symbol, 'Price': f"{last['Close']:.2f}", 'Signal': '⚡ GOLDEN BUY 🟢'})
                elif (last['RSI'] > 70) and (last['Close'] < last['EMA_200']) and (last['Close'] >= last['BB_Upper']):
                    results.append({'Stock': symbol, 'Price': f"{last['Close']:.2f}", 'Signal': '🔥 GOLDEN SELL 🔴'})
                
                # 1000 स्टॉक्स के लिए सर्वर को सांस लेने का समय दें
                time.sleep(0.1) 
                
            except: continue
        
        status_text.text("स्कैन पूरा हुआ!")
        
        if results:
            df = pd.DataFrame(results)
            df['Stock'] = df['Stock'].apply(make_clickable)
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("कोई सेटअप नहीं मिला।")
            
    except Exception as e:
        st.error(f"एरर: {e}")
