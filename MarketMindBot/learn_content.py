"""Topics of /learn command
Content topics live here, not in main.py
"""

LEARN_TOPICS = {
    "rsi": {
        "title": "RSI Nedir?",
        "text": "RSI (Göreceli Güç Endeksi), bir varlığın son dönemdeki fiyat hareketlerinin hızını ve büyüklüğünü ölçen bir teknik analiz göstergesidir. Genellikle 0 ile 100 arasında değer alır; 70'in üzeri aşırı alım, 30'un altı ise aşırı satım bölgesini işaret eder.",
    },
    "monthly_rate": {
        "title": "Aylık Oran (Monthly Rate) Nedir?",
        "text": "Aylık oran, bir varlığın fiyatında, gelirinde veya getirisinde son 30 günlük süre içerisinde gerçekleşen yüzde bazlı değişimi ifade eder. Yatırımcılara kısa-orta vadeli performans trendlerini ve varlığın aylık bazdaki ivmesini görme imkanı sağlar.",
    },
    "index": {
        "title": "Endeks (Index) Nedir?",
        "text": "Endeks, belirli bir piyasa, sektör veya varlık grubunun genel performansını ve fiyat hareketlerini toplu olarak ölçen istatistiksel bir göstergedir. Yatırımcıların piyasadaki genel yönü takip etmesine ve bireysel varlıkları piyasa ortalamasıyla karşılaştırmasına yardımcı olur.",
    },
    "volume_ratio": {
        "title": "Hacim Oranı Nedir?",
        "text": "Hacim oranı, bir hissenin bugünkü işlem hacminin son bir aylık ortalama hacmine bölünmesiyle bulunur. 1.0 değeri, bugün ortalama kadar işlem yapıldığı anlamına gelir; 1.5 gibi bir değer ortalamanın belirgin şekilde üzerinde bir ilgi olduğunu, 0.7 gibi bir değer ise günün sönük geçtiğini gösterir. Aynı fiyat hareketi, yüksek hacimle gerçekleştiğinde daha geniş bir katılımla, düşük hacimle gerçekleştiğinde ise daha az sayıda işlemle oluşmuş demektir.",
    },
    "delay": {
        "title": "Veriler Neden 15 Dakika Gecikmeli?",
        "text": "Bu bot, ücretsiz bir veri kaynağı kullanıyor ve borsaların anlık fiyat akışı lisanslı bir hizmet olduğu için veriler yaklaşık 15 dakika gecikmeli geliyor. Bu, gördüğün fiyatın 15 dakika önceki fiyat olduğu anlamına gelir. Aynı durum alarmlar için de geçerlidir: kurduğun hedefe ulaşıldığında bildirim, o hareketin veriye yansımasından sonra gelir, yani anlık değildir.",
    },
    "disclaimer": {
        "title": "Bot Neden Yatırım Tavsiyesi Vermiyor?",
        "text": "Türkiye'de yatırım tavsiyesi vermek, SPK tarafından yetkilendirilmiş kurum ve kişilere ait lisanslı bir faaliyettir. Bu bot lisanslı bir danışman değil, eğitim amaçlı bir projedir; bu yüzden verileri ve göstergeleri açıklar, ancak hiçbir zaman al, sat veya tut demez. Yapay zeka katmanı da bu kısıtla çalışacak şekilde tasarlandı: görevi sayıların ne anlattığını açıklamak, hangi hissenin daha iyi olduğunu söylemek değil. Tüm yatırım kararları ve sonuçları kullanıcıya aittir.",
    },
}