import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 1. पेज सेटअप
st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Stable Scanner")

# Google Sheet CSV लिंक
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=600)
def get_symbols():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        # नाम साफ करें और .NS जोड़ें
        return [str(s).strip() + '.NS' if '.NS' not in str(s) else str(s).strip() for s in df.iloc[:, 0].dropna().tolist()]
    except:
        return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'SBIN.NS']

def get_data(symbol):
    try:
        # डेटा फेच करें
        df = yf.download(symbol, period="1mo", interval="15m", progress=False)
        if df.empty or len(df) < 21: return None
        
        # EMA कैलकुलेशन
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df
    except:
        return None

# 2. स्कैनिंग लॉजिक
if st.button("🚀 सुरक्षित स्कैन शुरू करें"):
    symbols = get_symbols()
    results = []
    
    # प्रोग्रेस बार जोड़े ताकि पता रहे स्कैन चल रहा है
    progress_bar = st.progress(0)
    
    with st.spinner('स्टॉक्स स्कैन हो रहे हैं (सर्वर सुरक्षा के लिए धीरे काम कर रहा है...)'):
        for i, symbol in enumerate(symbols):
            df = get_data(symbol)
            if df is not None:
                # सुरक्षित वैल्यू एक्सट्रैक्शन
                curr_price = float(df['Close'].iloc[-1])
                curr_e9 = float(df['EMA9'].iloc[-1])
                curr_e21 = float(df['EMA21'].iloc[-1])
                prev_e9 = float(df['EMA9'].iloc[-2])
                prev_e21 = float(df['EMA21'].iloc[-2])
                
                signal = "⚪ WAIT"
                if prev_e9 <= prev_e21 and curr_e9 > curr_e21: signal = "🟢 BUY"
                elif prev_e9 >= prev_e21 and curr_e9 < curr_e21: signal = "🔴 SELL"
                
                if signal != "⚪ WAIT":
                    results.append({'Stock': symbol, 'Signal': signal, 'Price': round(curr_price, 2)})
            
            # हर स्टॉक के बाद 1 सेकंड का ब्रेक (Rate Limit से बचने के लिए)
            time.sleep(1)
            progress_bar.progress((i + 1) / len(symbols))
        
        # 3. परिणाम दिखाना
        if results:
            res_df = pd.DataFrame(results)
            st.dataframe(res_df, use_container_width=True)
            st.success(f"स्कैन पूरा हुआ। {len(results)} स्टॉक्स में एक्शन है।")
        else:
            st.info("अभी किसी स्टॉक में क्रॉसओवर सिग्नल नहीं है (सिर्फ सिग्नल वाले स्टॉक्स दिखाए जाते हैं)।")
