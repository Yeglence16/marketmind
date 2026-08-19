def rate_to_color(changing_rate: float) -> int:
    """Değişim oranına göre embed rengi (TradingView konvansiyonu)."""
    if changing_rate > 0:
        return 0x04d13b   # yeşil — yükseliş
    elif changing_rate == 0:
        return 0x696969   # gri — değişim yok
    return 0xd10404
    
# helpers.py
def rate_to_emoji(changing_rate: float) -> str:
    if changing_rate > 0:
        return "📈"
    elif changing_rate == 0:
        return "➖"
    return "📉"