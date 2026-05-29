import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Lite Mode")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=600)
def get_symbols():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        return df.iloc[:, 0].dropna().astype(str).tolist()
    except:
        return ['RELIANCE.NS', 'TCS.NS']

def get_data(symbol):
    try:
        # केवल 5 दिन का डेटा - बहुत हल्का
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        if len(df) < 21: return None
        
        # सिर्फ EMA कैलकुलेशन
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df.iloc[-2:] # सिर्फ आखिरी 2 रो चाहिए
    except:
        return None

if st.button("🚀 स्कैन शुरू करें"):
    symbols = get_symbols()
    results = []
    
    with st.spinner('स्कैनिंग...'):
        for symbol in symbols:
            df = get_data(symbol)
            if df is None: continue
            
            # सुरक्षित वैल्यू एक्सट्रैक्शन
            try:
                p_e9, p_e21 = float(df['EMA9'].iloc[0]), float(df['EMA21'].iloc[0])
                c_e9, c_e21 = float(df['EMA9'].iloc[1]), float(df['EMA21'].iloc[1])
                price = float(df['Close'].iloc[1])
                
                signal = "⚪"
                if p_e9 <= p_e21 and c_e9 > c_e21: signal = "🟢 BUY"
                elif p_e9 >= p_e21 and c_e9 < c_e21: signal = "🔴 SELL"
                
                if signal != "⚪":
                    results.append({'Stock': symbol, 'Signal': signal, 'Price': round(price, 2)})
            except: continue
        
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.write("अभी कोई सिग्नल नहीं मिला।")
