import yfinance as yf
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo          # stdlib, no install needed

IST = ZoneInfo("Europe/Istanbul")      # BIST's own clock, not the server's


def is_market_open() -> bool:
    """
    Şu an BIST açık mı? Hafta sonu ve saat kontrolü yapar.
    Resmi tatilleri kontrol etmez (şimdilik).
    """
    time_check = datetime.now(IST)
    
    
    if time_check.weekday() >= 5:  # Cumartesi veya Pazar
        return False
    
    # BIST 10:00-18:00 arası açık
    if time_check.hour < 10 or time_check.hour >= 18:
        return False
    
    return True

@dataclass
class Stock:
    symbol:str
    closing:float
    changing_rate:float
    date:str
    is_market_close:bool
    volume:int
    sector:str
    industry:str
    rsi:float
    monthly_rate:float
    volume_ratio:float
    
    _cache = {}
    
    
    @classmethod
    def get_stock(cls,symbol:str):
        symbol = symbol.upper()
        
        #cache'te taze veri var mı kontrolü
        if symbol in cls._cache:
            company,draw_time = cls._cache[symbol]
            
            elapsed_time = (datetime.now(IST) - draw_time).total_seconds()
            
            if elapsed_time < 300:  # 300 saniye = 5 dakika
                print(f"[CACHE] {symbol} hafızadan geldi")
                return company
            
        stock_name = symbol + ".IS"

        ticker = yf.Ticker(stock_name)
        data = ticker.history(period='1mo') 
        data = data.dropna(subset=['Close'])
        data = data[data['Volume'] > 0] 
        if data.empty:
            return None
        
        print(data.tail(3))
        
        delta = data["Close"].diff()
        
        gain = delta.where(delta>0,0)
        loss = -delta.where(delta<0,0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        last_rsi = rsi.iloc[-1]
        
        if avg_loss.iloc[-1] == 0 or pd.isna(last_rsi):
            last_rsi = None
        else:
            last_rsi = round(last_rsi, 2)
        
        #monthly change rate
        info = ticker.info      
        
        frow = data.iloc[0]
        lrow = data.iloc[-1]
        second_lrow = data.iloc[-2]
        
        m_rate = ((lrow['Close']-frow['Close']) / frow["Close"]) * 100
        c_rate = ((lrow['Close']-second_lrow['Close']) / second_lrow["Close"]) * 100
        
        #volume ratio
        
        avg_volume = data["Volume"].mean()
        volume_ratio = lrow["Volume"]/avg_volume
        
        
        
        company = cls(
            symbol=symbol,
            closing=lrow['Close'],
            changing_rate=round(c_rate, 2),
            date=str(lrow.name),
            is_market_close=not is_market_open(),
            volume=int(lrow['Volume']),
            sector=info.get("sector", "Bilinmiyor"),
            industry=info.get("industry", "Bilinmiyor"),
            rsi=last_rsi,
            monthly_rate=round(m_rate,2),
            volume_ratio=round(volume_ratio,2)
        )
        
        print(f"[YAHOO] {symbol} internetten çekildi")
        cls._cache[symbol] = (company, datetime.now(IST))
        return company
        
