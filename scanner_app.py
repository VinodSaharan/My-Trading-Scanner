import streamlit as st
import yfinance as yf
import pandas as pd

# 1. पेज सेटअप
st.set_page_config(page_title="Intrabullscanner22", layout="wide")

st.markdown("""
    <style>
        .stButton>button {width: 100%; height: 80px; font-size: 24px; font-weight: bold; background-color: #2E86C1; color: white; border-radius: 10px;}
        [data-testid="stDataFrame"] {width: 100% !important;}
    </style>
""", unsafe_allow_html=True)

st.title("📈 Intrabullscanner22 | Pro Terminal")

# Google Sheet लिंक
SHEET_URL= "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data(ttl=600)
def get_symbols():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        stocks = df.iloc[:, 0].dropna().astype(str).tolist()
        return [s.strip() if '.NS' in s else s.strip() + '.NS' for s in stocks]
    except:
        return ['RELIANCE.NS', 'TCS.NS']

def get_data(symbol):
    try:
        # डेटा डाउनलोड
        df = yf.download(symbol, period="5d", interval="15m", progress=False)
        if df.empty or len(df) < 21: return None
        
        # EMA और RSI कैलकुलेशन
        df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 0.0001))))
        
        return df.fillna(0)
    except:
        return None

# 2. मुख्य स्कैनिंग
if st.button("🚀 लाइव स्कैन शुरू करें"):
    symbols = get_symbols()
    results = []
    
    with st.spinner('डेटा फेच हो रहा है...'):
        for symbol in symbols:
            df = get_data(symbol)
            if df is None: continue
            
            # .iloc के बाद सीधे वैल्यू निकालें (Series का उपयोग न करें)
            curr = df.iloc[-1]
            prev = df.iloc[-2]
            
          p_e9 = float(prev['EMA9'].iloc[0]) if hasattr(prev['EMA9'], 'iloc') else float(prev['EMA9'])
            p_e21 = float(prev['EMA21'].iloc[0]) if hasattr(prev['EMA21'], 'iloc') else float(prev['EMA21'])
            c_e9 = float(curr['EMA9'].iloc[0]) if hasattr(curr['EMA9'], 'iloc') else float(curr['EMA9'])
            c_e21 = float(curr['EMA21'].iloc[0]) if hasattr(curr['EMA21'], 'iloc') else float(curr['EMA21'])
            
            signal = "⚪ WAIT"
            if p_e9 <= p_e21 and c_e9 > c_e21: signal = "🟢 BUY"
            elif p_e9 >= p_e21 and c_e9 < c_e21: signal = "🔴 SELL"
            
            results.append({
                'Stock': symbol, 
                'Signal': signal, 
                'Price': round(float(curr['Close']), 2), 
                'RSI': round(float(curr['RSI']), 2)
            })
        
        # 3. टेबल रेंडरिंग
        if results:
            res_df = pd.DataFrame(results)
            def style_table(val):
                color = 'green' if val == '🟢 BUY' else 'red' if val == '🔴 SELL' else 'black'
                return f'color: {color}; font-weight: bold; font-size: 18px;'
            
            st.dataframe(res_df.style.map(style_table, subset=['Signal']), use_container_width=True)
        else:
            st.warning("कोई डेटा नहीं मिला। स्टॉक्स की स्पेलिंग या Google Sheet चेक करें।")
