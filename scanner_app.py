import streamlit as st
import yfinance as yf
import pandas as pd

# 1. पेज का टाइटल
st.title("मेरा स्टॉक स्कैनर 📈")

# 2. अपनी Google Sheet का Public CSV लिंक यहाँ डालें
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSpVHs0moYjed1jNIJT64sMjDkZSCa1BAAIynZqh3uodODA06TJ37f-znybktZasqhnZD8t09BTJcyr/pub?output=csv"

@st.cache_data # इससे ऐप बार-बार डेटा डाउनलोड नहीं करेगा (स्पीड बढ़ेगी)
def load_data(url):
    df = pd.read_csv(url)
    # पक्का करें कि आपकी शीट के कॉलम का नाम 'Symbol' है
    return df['Symbol'].dropna().tolist()

symbols = load_data(url)

if st.button("स्कैन करें"):
    with st.spinner('डेटा डाउनलोड हो रहा है...'):
        # 3. डेटा डाउनलोड करना
        data = yf.download(symbols, period="2d", group_by='column', threads=True)
        
        results = []
        
        # 4. डेटा स्कैनिंग लॉजिक
        for symbol in symbols:
            try:
                # यहाँ हमने डेटा को सही तरीके से एक्सेस किया है
                current_price = data['Close'][symbol].iloc[-1]
                prev_close = data['Close'][symbol].iloc[-2]
                
                # अगर आज का दाम कल से ज्यादा है
                if current_price > prev_close:
                    change = ((current_price - prev_close) / prev_close) * 100
                    results.append({
                        'Stock': symbol, 
                        'Price': round(float(current_price), 2), 
                        'Change %': round(float(change), 2)
                    })
            except Exception:
                continue
        
        # 5. रिजल्ट दिखाना
        if results:
            res_df = pd.DataFrame(results)
            st.success(f"कुल {len(res_df)} स्टॉक्स बढ़त में हैं!")
            st.table(res_df.sort_values(by='Change %', ascending=False))
        else:
            st.warning("आज कोई स्टॉक बढ़त में नहीं मिला।")

# यह समझने के लिए कि डेटा कैसे स्ट्रक्चर होता है
st.write("---")
st.caption("नोट: सुनिश्चित करें कि आपने Google Sheet को 'Publish to web' किया है।")
