import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Pro Stock Scanner", layout="wide")
st.title("🚀 एडवांस्ड स्टॉक स्कैनर (RSI + Filter)")

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

# RSI कैलकुलेशन फंक्शन
def get_rsi(hist, period=14):
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

if st.button("🚀 RSI फिल्टर के साथ स्कैन शुरू करें"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        
        results = []
        progress_bar = st.progress(0) # 1. प्रोग्रेस बार
        
        for i, symbol in enumerate(all_symbols):
            try:
                hist = yf.download(symbol, period="1mo", interval="1d", progress=False, timeout=5)
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                
                if len(hist) > 14:
                    # RSI कैलकुलेशन
                    hist['RSI'] = get_rsi(hist)
                    last_rsi = hist['RSI'].iloc[-1]
                    last_price = hist['Close'].iloc[-1]
                    
                    # 2. फिल्टर: केवल वही स्टॉक दिखाएं जिनका RSI < 30 (Oversold) या > 70 (Overbought)
                    # यहाँ आप अपनी पसंद का फिल्टर लगा सकते हैं
                    if last_rsi < 30: # 'Buy' सिग्नल (Oversold)
                        results.append({'Stock': symbol, 'Price': f"{float(last_price):.2f}", 'RSI': f"{float(last_rsi):.2f}", 'Signal': 'BUY (Oversold)'})
            except: continue
            
            # प्रोग्रेस बार अपडेट करें
            progress_bar.progress((i + 1) / len(all_symbols))
            
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("कोई स्टॉक इस RSI फिल्टर में फिट नहीं बैठा।")
            
    except Exception as e:
        st.error(f"एरर: {e}")
