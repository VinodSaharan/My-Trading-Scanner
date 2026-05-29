import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Stable Pro")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"
@st.cache_data(ttl=600)
def get_symbols():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        return [str(s).strip() + '.NS' if '.NS' not in str(s) else str(s).strip() for s in df.iloc[:, 0].dropna().tolist()]
    except:
        return ['RELIANCE.NS', 'TCS.NS']

def get_data(symbol):
    try:
        df = yf.download(symbol, period="1mo", interval="15m", progress=False)
        if df.empty or len(df) < 21: return None
        
        # EMA कैलकुलेशन
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except:
        return None

if st.button("🚀 स्कैन शुरू करें"):
    symbols = get_symbols()
    results = []
    progress_bar = st.progress(0)
    
    with st.spinner('डेटा प्रोसेस हो रहा है...'):
        for i, symbol in enumerate(symbols):
            df = get_data(symbol)
            if df is not None:
                try:
                    # .iloc[-1] के बाद .squeeze() का उपयोग किया है, जो किसी भी फॉर्मेट (Series/Array) को सीधे नंबर बना देता है
                    curr_price = float(df['Close'].iloc[-1].squeeze())
                    curr_e9 = float(df['EMA9'].iloc[-1].squeeze())
                    curr_e21 = float(df['EMA21'].iloc[-1].squeeze())
                    prev_e9 = float(df['EMA9'].iloc[-2].squeeze())
                    prev_e21 = float(df['EMA21'].iloc[-2].squeeze())
                    
                    signal = "⚪"
                    if prev_e9 <= prev_e21 and curr_e9 > curr_e21: signal = "🟢 BUY"
                    elif prev_e9 >= prev_e21 and curr_e9 < curr_e21: signal = "🔴 SELL"
                    
                    if signal != "⚪":
                        results.append({'Stock': symbol, 'Signal': signal, 'Price': round(curr_price, 2)})
                except Exception:
                    continue
            
            time.sleep(1) # सर्वर को ब्लॉक होने से बचाने के लिए
            progress_bar.progress((i + 1) / len(symbols))
        
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("फिलहाल किसी स्टॉक में सिग्नल नहीं है।")
