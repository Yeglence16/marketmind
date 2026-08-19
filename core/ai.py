import os                          # .env'den key okumak için
from dotenv import load_dotenv     # .env yükleyici
from google import genai           # Gemini SDK
from core.data import Stock        # AI, Stock yapısını tanımalı (tip ipucu için)
from google.genai import errors  
from google.genai import types

load_dotenv()
client = genai.Client(api_key = os.getenv("GEMINI_API_KEY")) #Gemini kapısı

def comment_stock(stock:Stock) -> str:
    
    rsi_text = f"{stock.rsi}" if stock.rsi is not None else "veri yok"
    market_status = "Kapalı" if stock.is_market_close else "Açık"
    volume_text = f"ortalamanın {stock.volume_ratio} katı"   # 1.0 = normal, >1.5 hareketli, <0.7 sönük
    
    prompt = f"""Sen BIST hisselerini eğitim amaçlı analiz eden bir asistansın.
Sana verilen verinin ne anlama geldiğini açıkla ve mevcut durumu yorumla.

İşte analiz edeceğin hisse verisi:
Hisse: {stock.symbol}  
Kapanış: {stock.closing} TL
1 Günlük Değişim: %{stock.changing_rate}
Tarih: {stock.date}
Borsa durumu: {market_status}
Hacim: {stock.volume}
Sektör: {stock.sector}
Alt sektör: {stock.industry}
RSI (14 günlük): {rsi_text}  (0-100 arası: 70 üzeri aşırı alım, 30 altı aşırı satım, arası nötr bölge)
1 Aylık değer değişim :  %{stock.monthly_rate}
Hacim Durumu (bugün vs aylık ortalama) : {volume_text}

Kurallar:
- SAKIN AL/SAT/TUT gibi yatırım tavsiyeleri verme, sadece eğitim amaçlı analiz yap.
- SADECE sana verilen verileri kullan; veri yoksa yeni veri üretme, "veri yok" de.
- Sadece verilen hisse hakkında konuş, başka konuya girme.
- En fazla 10 cümle yaz, madde kullanma, tek paragraf yaz, başlık yapma, doğrudan analize gir.
- Metrikleri tek tek sıralama; birbiriyle ilişkilendirerek tek bir bütünsel resim çiz (örn. RSI, aylık eğilim ve hacmi birlikte değerlendir).
"""
    
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        
        usage = response.usage_metadata
        print(f"[TOKEN] giden: {usage.prompt_token_count} | gelen: {usage.candidates_token_count} | toplam: {usage.total_token_count}")
        
        return response.text
    
    except errors.APIError as  e:
        print(f"Gemini Hata verdi:{e}")
        return None


def comment_compare(stock_1: Stock, stock_2: Stock) -> str:

    # both RSI values can be None -> format only when they exist
    rsi_1 = f"{stock_1.rsi}" if stock_1.rsi is not None else "veri yok"
    rsi_2 = f"{stock_2.rsi}" if stock_2.rsi is not None else "veri yok"
    market_status = "Kapalı" if stock_1.is_market_close else "Açık"

    prompt =     prompt = f"""Sen BIST hisselerini eğitim amaçlı analiz eden bir asistansın.
Sana verilen iki hissenin verisini karşılaştır ve farkların ne anlama geldiğini açıkla.

BİRİNCİ HİSSE
Hisse: {stock_1.symbol}
Kapanış: {stock_1.closing} TL
1 Günlük Değişim: %{stock_1.changing_rate}
RSI (14 günlük): {rsi_1}
Hacim Durumu (bugün vs aylık ortalama): ortalamanın {stock_1.volume_ratio} katı
1 Aylık Değişim: %{stock_1.monthly_rate}
Sektör: {stock_1.sector}
Alt sektör: {stock_1.industry}

İKİNCİ HİSSE
Hisse: {stock_2.symbol}
Kapanış: {stock_2.closing} TL
1 Günlük Değişim: %{stock_2.changing_rate}
RSI (14 günlük): {rsi_2}
Hacim Durumu (bugün vs aylık ortalama): ortalamanın {stock_2.volume_ratio} katı
1 Aylık Değişim: %{stock_2.monthly_rate}
Sektör: {stock_2.sector}
Alt sektör: {stock_2.industry}

Borsa durumu: {market_status}
RSI ölçeği: 0-100 arası, 70 üzeri aşırı alım, 30 altı aşırı satım, arası nötr bölge.

Kurallar:
- Görevin iki hissenin verilerindeki FARKLARIN ne anlama geldiğini eğitim amaçlı açıklamaktır. İki hissenin RSI, aylık eğilim ve hacim durumu birbirinden nerede ayrışıyor, bu ayrışma teknik olarak neyi gösterir, bunu anlat.
- Bir hissenin hacmi ortalamasının altındayken diğerininki normal seviyedeyse bunun ne anlama geldiğini açıkla. Aynı şeyi RSI ve aylık eğilim için de yap.
- Sayıları tekrar etmek zorunda değilsin; kullanıcı sayıları zaten üstteki tabloda görüyor. Sen sayıların ne anlattığını yaz.
- SAKIN AL/SAT/TUT gibi yatırım tavsiyeleri verme.
- Hangi hissenin daha iyi, daha cazip veya daha güçlü olduğunu söyleme. Farkı tarif et, taraf tutma.
- İki hissenin TL fiyatını birbiriyle kıyaslama; farklı sermaye yapıları nedeniyle anlamsızdır.
- SADECE verilen bu iki hisseyi konu al; üçüncü bir hisseye, endekse veya sektör ortalamasına atıf yapma.
- SADECE verilen verileri kullan; veri yoksa "veri yok" de. Gelecek tahmini yapma.
- En fazla 10 cümle, tek paragraf, madde yok, başlık yok, doğrudan analize gir.
- İki hissenin bir metrikte belirgin farkı yoksa o metriği anlatmak zorunda değilsin; en az bir metrik farkı yoksa bunu söyle.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2)
        )
        usage = response.usage_metadata
        print(f"[TOKEN] giden: {usage.prompt_token_count} | gelen: {usage.candidates_token_count} | toplam: {usage.total_token_count}")
        return response.text

    except errors.APIError as e:
        print(f"Gemini Hata verdi:{e}")
        return None
    
    
if __name__ == "__main__":
    comment = comment_stock(Stock.get_stock("THYAO"))
    print(comment)