# पुराने कोड की जगह यह इस्तेमाल करें:
try:
    hist = yf.download(symbol, period="1d", interval="15m", progress=False, timeout=5)
    
    # 1. कॉलम फिक्स करें (मल्टी-इंडेक्स समस्या का हल)
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = hist.columns.get_level_values(0)
    
    if not hist.empty:
        # 2. .iloc[-1] के बाद सीधे वैल्यू निकालें (Scalar value)
        last_price = hist['Close'].iloc[-1]
        
        # 3. पक्का करें कि यह एक सिंगल नंबर (float) है
        if isinstance(last_price, pd.Series):
            last_price = last_price.iloc[0]
            
        results.append({'Stock': symbol, 'Price': f"{float(last_price):.2f}"})
except Exception as e:
    continue
