import pandas as pd
import json
import yfinance as yf
import time

df = pd.read_excel(r"C:\Users\HP VICTUS\Downloads\Şirketler.xlsx",
                header=None,
                usecols="A:B") #gerekli sütunları al ve excel dosyasını dataframe yap

df.columns = ["Code","Company"] #sütun isimlerini belirle
df.dropna(inplace=True)#boş satırları at
df.drop(2, inplace=True)#gereksiz satırı at

#dataframe temiz mi kontrol et
#print(df.head(100))

#dataframe bilgilerini kontrol et
#print(df.info())



comp_dict = dict()

for code, name in zip(df["Code"], df["Company"]):
    items = code.split(",")
    
    for item in items:
        
        try:
            cleansed = item.strip()
            ticker = yf.Ticker(cleansed + ".IS")
            data = ticker.history(period="1mo")
            data = data[data["Volume"] > 0]
            
            if not data.empty:
                comp_dict[cleansed] = name
        
            else:
                print(cleansed)

        except Exception as e:
            print(f"[HATA] {cleansed}: {e}") 
    
        time.sleep(2)
        
print(len(comp_dict))

    
with open("MarketMindBot/companies.json","w",encoding="utf-8") as f:
    json.dump(comp_dict, f, ensure_ascii=False, indent=2)