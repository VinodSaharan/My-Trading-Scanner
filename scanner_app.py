import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📈 VWAP Crossover Scanner")

def scan_stocks(symbols):
    results = []
    for symbol in symbols:
        try:
            # 15 मिनट के चार्ट पर डेटा
            hist = yf.download(symbol, period="2d", interval="15m", progress=False)
            if len(hist) < 2: continue
            
            # VWAP कैलकुलेशन
            hist['TP'] = (hist['High'] + hist['Low'] + hist['Close']) / 3
            hist['VWAP'] = (hist['TP'] * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            
            # Crossover Condition: पिछली कैंडल VWAP के नीचे थी, करंट ऊपर है
            prev_close = hist['Close'].iloc[-2]
            prev_vwap = hist['VWAP'].iloc[-2]
            curr_close = hist['Close'].iloc[-1]
            curr_vwap = hist['VWAP'].iloc[-1]
            
            if prev_close < prev_vwap and curr_close > curr_vwap:
                results.append({'Stock': symbol, 'Price': f"{float(curr_close):.2f}", 'Signal': 'VWAP Breakout'})
        except: continue
    return results

if st.button("🚀 Crossover स्कैन शुरू करें"):
    # यहाँ अपने स्टॉक्स डालें
    all_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'SBIN.NS', 'HDFCBANK.NS'] 
    
    data = scan_stocks(all_symbols)
    if data:
        st.dataframe(pd.DataFrame(data))
    else:
        st.warning("अभी कोई Crossover नहीं मिला।")
