import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Live Auto-Refresh")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=60) # डेटा को 60 सेकंड में रिफ्रेश करें
def get_data_for_all(symbols):
    results = []
    tickers = yf.Tickers(" ".join(symbols))
    for symbol in symbols:
        try:
            hist = tickers.tickers[symbol].history(period="1mo", interval="15m")
            if len(hist) > 21:
                hist['EMA9'] = hist['Close'].ewm(span=9, adjust=False).mean()
                hist['EMA21'] = hist['Close'].ewm(span=21, adjust=False).mean()
                
                curr_p = float(hist['Close'].iloc[-1].squeeze())
                prev_p = float(hist['Close'].iloc[-2].squeeze())
                curr_e9 = float(hist['EMA9'].iloc[-1].squeeze())
                curr_e21 = float(hist['EMA21'].iloc[-1].squeeze())
                prev_e9 = float(hist['EMA9'].iloc[-2].squeeze())
                prev_e21 = float(hist['EMA21'].iloc[-2].squeeze())
                
                change_pct = ((curr_p - prev_p) / prev_p) * 100
                
                if (prev_e9 <= prev_e21 and curr_e9 > curr_e21) or (prev_e9 >= prev_e21 and curr_e9 < curr_e21):
                    signal = "🟢 BUY" if curr_e9 > curr_e21 else "🔴 SELL"
                    results.append({
                        'Stock': symbol, 'Signal': signal, 
                        'Price': f"{curr_p:.2f}", 'Change %': f"{change_pct:.2f}%"
                    })
        except: continue
    return results

# मुख्य लूप
symbols_df = pd.read_csv(SHEET_URL, header=None)
symbols = [str(s).strip() + '.NS' if '.NS' not in str(s) else str(s).strip() for s in symbols_df.iloc[:, 0].dropna().tolist()]

placeholder = st.empty()

# ऑटो-रिफ्रेश लूप
while True:
    with placeholder.container():
        results = get_data_for_all(symbols)
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("कोई सिग्नल नहीं। रिफ्रेश हो रहा है...")
        st.write(f"अंतिम अपडेट: {time.strftime('%H:%M:%S')}")
    
    time.sleep(60) # 60 सेकंड का इंतज़ार
    st.rerun()
