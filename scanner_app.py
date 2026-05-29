import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Intrabullscanner22", layout="wide")
st.title("📈 Intrabullscanner22 | Debug Mode")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=600)
def get_symbols():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        return df.iloc[:, 0].dropna().astype(str).tolist()
    except:
        return ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'SBIN.NS']

def get_data(symbol):
    try:
        # 1 महीने का डेटा लें ताकि क्रॉसओवर की संभावना बढ़े
        df = yf.download(symbol, period="1mo", interval="15m", progress=False)
        if len(df) < 21: return None
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        return df.iloc[-2:] 
    except:
        return None

if st.button("🚀 स्कैन शुरू करें"):
    symbols = get_symbols()
    all_data = []
    
    with st.spinner('स्टॉक्स एनालाइज हो रहे हैं...'):
        for symbol in symbols:
            df = get_data(symbol)
            if df is None: continue
            
            p_e9, p_e21 = float(df['EMA9'].iloc[0]), float(df['EMA21'].iloc[0])
            c_e9, c_e21 = float(df['EMA9'].iloc[1]), float(df['EMA21'].iloc[1])
            price = float(df['Close'].iloc[1])
            
            signal = "⚪ WAIT"
            if p_e9 <= p_e21 and c_e9 > c_e21: signal = "🟢 BUY"
            elif p_e9 >= p_e21 and c_e9 < c_e21: signal = "🔴 SELL"
            
            all_data.append({'Stock': symbol, 'Signal': signal, 'Price': round(price, 2)})
        
        # यहाँ पूरा डेटा टेबल में दिखेगा, चाहे सिग्नल हो या न हो
        if all_data:
            st.dataframe(pd.DataFrame(all_data), use_container_width=True)
            st.success(f"कुल {len(all_data)} स्टॉक्स स्कैन किए गए।")
        else:
            st.warning("कोई डेटा नहीं मिला।")
