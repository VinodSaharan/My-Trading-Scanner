import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Golden Combo Pro-Scanner", layout="wide")
st.title("🚀 गोल्डन कॉम्बो प्रो-स्कैनर")

# अपना Google Sheet लिंक यहाँ डालें
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

# 1. इंडिकेटर्स कैलकुलेशन फंक्शन
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

# 2. स्टाइलिंग और लिंक फंक्शन
def highlight_signals(val):
    if 'BUY' in val: return 'background-color: #006400; color: white'
    if 'SELL' in val: return 'background-color: #8B0000; color: white'
    return ''

def make_clickable(symbol):
    url = f"https://www.tradingview.com/chart/?symbol={symbol}"
    return f'<a target="_blank" href="{url}" style="color: blue;">{symbol}</a>'

# 3. मुख्य स्कैनिंग लॉजिक
if st.button("🔍 मार्केट स्कैन करें", type="primary"):
    try:
        symbols_df = pd.read_csv(SHEET_URL, header=None)
        all_symbols = symbols_df.iloc[:, 0].dropna().tolist()
        results = []
        status_text = st.empty()
        
        for i, symbol in enumerate(all_symbols):
            status_text.text(f"स्कैनिंग: {i+1}/{len(all_symbols)} - {symbol}")
            try:
                # स्विंग ट्रेडिंग के लिए daily डेटा
                hist = yf.download(symbol, period="2y", interval="1d", progress=False, timeout=5)
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                hist = get_indicators(hist)
                
                last = hist.iloc[-1]
                signal = ""
                
                # गोल्डन कॉम्बो लॉजिक
                if (last['RSI'] < 30) and (last['Close'] > last['EMA_200']) and (last['Close'] <= last['BB_Lower']):
                    signal = '⚡ GOLDEN BUY 🟢'
                elif (last['RSI'] > 70) and (last['Close'] < last['EMA_200']) and (last['Close'] >= last['BB_Upper']):
                    signal = '🔥 GOLDEN SELL 🔴'
                
                if signal:
                    results.append({'Stock': symbol, 'Price': f"{last['Close']:.2f}", 'RSI': f"{last['RSI']:.1f}", 'Signal': signal})
            except: continue
        
        status_text.text("स्कैन पूरा हुआ!")
        
        if results:
            df = pd.DataFrame(results)
            # स्टॉक कॉलम को लिंक में बदलें
            df['Stock'] = df['Stock'].apply(make_clickable)
            # HTML रेंडरिंग
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("अभी कोई गोल्डन सेटअप नहीं मिला।")
    except Exception as e:
        st.error(f"एरर: {e}")
