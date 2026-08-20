"""Shared formatting helpers — colour and emoji rules live here, not in main.py."""

def rate_to_color(changing_rate: float) -> int:
    """Embed colour for a change rate — green up, red down (TradingView convention)."""
    if changing_rate > 0:
        return 0x04d13b   # green — increasing
    elif changing_rate == 0:
        return 0x696969   # grey — no change
    return 0xd10404       # red - decreasing

    
def rate_to_emoji(changing_rate: float) -> str:
    """Trend emoji for a change rate."""
    if changing_rate > 0:
        return "📈"
    elif changing_rate == 0:
        return "➖"
    return "📉"