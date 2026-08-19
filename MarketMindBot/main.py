import os #dosyalara eriş
from dotenv import load_dotenv #.env dosyasını okuyan aracı içeri aktar
import discord #discord kütüphanesini çağır
from discord.ext import commands #komut yönetimi uzantısını içe aktar
from core.data import Stock,is_market_open
from discord import app_commands
from core.ai import comment_stock
import json
from MarketMindBot.helpers import rate_to_color,rate_to_emoji
from core.database import (
    init_db, add_alarm, get_user_alarms, get_all_alarms, delete_alarm
)
from discord.ext import tasks
from MarketMindBot.learn_content import LEARN_TOPICS
from core.ai import comment_stock, comment_compare


with open("MarketMindBot/companies.json","r",encoding="utf-8") as f:
    companies = json.load(f)

#env dosyasını çevir
load_dotenv() #.env dosyasını oku ve kullanıma hazırla
TOKEN = os.getenv("DISCORD_TOKEN") #DISCORD_TOKEN key'inin valuesunu al

intents = discord.Intents.default() #sadece temel izinler, hassas/privileged bilgilere talip degil
bot = commands.Bot(command_prefix="!", intents = intents) #zorunlu bir prefix ve default intents

#botu discorda bağlar
@bot.event
async def on_ready():
    print(f"{bot.user} olarak giriş yapıldı. MarketMind çevrimiçi!")
    init_db()                              # ← alarms.db + tablo hazır olsun
    synced = await bot.tree.sync()         # ← sonra Discord'a yükle
    print(f"{len(synced)} slash komut senkronize edildi")
    
    if not alarm_checker.is_running():
        alarm_checker.start()
        print(f"🔔 Alarm döngüsü başladı ({CHECK_INTERVAL_MINUTES} dk periyot)")    

#komut-1
@bot.tree.command(name ="lebron", description = "Cleveland halkının LeBron şarkısı") #komut ismi ve açıklamasını yaz
async def lebron(interaction: discord.Interaction): #komut çalisinca tetiklenir
    await interaction.response.send_message("https://www.youtube.com/watch?v=KVtqZgfFKgQ&t=1s") #outputu ver

#---- LATEST VALUE ----
@bot.tree.command(name = "latest_value",description="Hissenin borsadaki en güncel değeri")
@app_commands.describe(symbol="BIST hisse sembolü, örn: AKBNK")
async def latest_value(interaction:discord.Interaction,symbol:str):
    await interaction.response.defer()                     
    sonuc = Stock.get_stock(symbol)

    if sonuc is None:
        
        embed_error = discord.Embed(
            title=f"❌HATA",
            description=f"❔`{symbol.upper()}` için veri bulunamadı. Sembolü kontrol et.",
            color=0xf5fc12
        )
        
        embed_error.set_footer(icon_url=interaction.client.user.display_avatar.url,
                            text="MarketMind")
        
        await interaction.followup.send(embed=embed_error)
        return
    rsi_text = f"{sonuc.rsi:.2f}" if sonuc.rsi is not None else "veri yok"
    color = rate_to_color(sonuc.changing_rate)
    
    embed = discord.Embed(
        title=f"📊 {sonuc.symbol}",
        
        description=f""" 
💰 Fiyat: {sonuc.closing:.2f} TL
{rate_to_emoji(sonuc.changing_rate)} Değişim: %{sonuc.changing_rate:.2f}
📊 RSI: {rsi_text}
🔊 Hacim: {sonuc.volume:,.0f} lot
🏭 Sektör: {sonuc.sector}
🏢 Endüstri: {sonuc.industry}
⚖️ Hacim Oranı: {sonuc.volume_ratio:.2f}x
🗓️ Aylık Değişim: %{sonuc.monthly_rate:.2f}
""",
        color=color
    )
    
    embed.add_field(
        name="📅 Veri Tarihi",
        value= sonuc.date[:10],
        inline=True
    )
    
    embed.add_field(
        name="🏦 Borsa Durumu",
        value="🟢 Borsa Açık,⏱️ Piyasa açıkken veriler ~15dk gecikmeli gelir" if sonuc.is_market_close == False else "🔴 Borsa Kapalı, Son kapanış verisi",
        inline=True
    )
    
    
    embed.set_footer(text="MarketMind",
                    icon_url=interaction.client.user.display_avatar.url)
    await interaction.followup.send(embed=embed)


#---- STOCK VALUATION ----
@bot.tree.command(name="stock_valuation",description="Son 1 Ay verisine bağlı AI yorumu(yatırım tavsiyesi değildir)" )
@app_commands.describe(symbol="BIST hisse sembolü, örn:AKBNK")
async def stock_valuation(interaction:discord.Interaction,symbol:str):
    await interaction.response.defer()
    
    sonuc = Stock.get_stock(symbol)
    
    if sonuc is None:
        
        embed_error = discord.Embed(
            title=f"❌HATA",
            description=f"❔`{symbol.upper()}` için veri bulunamadı. Sembolü kontrol et.",
            color=0xf5fc12
        )
        
        embed_error.set_footer(icon_url=interaction.client.user.display_avatar.url,
                            text="MarketMind")
        
        await interaction.followup.send(embed=embed_error)
        return


        
    comment = comment_stock(sonuc)
    

    
    if comment is None:
        
        embed_none = discord.Embed(
            title=f"❌HATA",
            description="⚠️ Bot yanıt veremedi.Lütfen daha sonra tekrar deneyin.",
            color=0xf5fc12
        )
        
        embed_none.set_footer(icon_url=interaction.client.user.display_avatar.url,
                            text="MarketMind")
        await interaction.followup.send(embed=embed_none) 
        return       
    
    if len(comment) > 4096:
        comment = comment[:4093] + "..."
    
    color = rate_to_color(sonuc.changing_rate)
    
    embed = discord.Embed(
        title=f"📊 {sonuc.symbol}",
        description=comment,
        color=color
    )
    
    embed.add_field(
        name="📅 Veri Tarihi",
        value= sonuc.date[:10],
        inline=True
    )
    
    embed.add_field(
        name="🏦 Borsa Durumu",
        value="🟢 Borsa Açık,⏱️ Piyasa açıkken veriler ~15dk gecikmeli gelir" if sonuc.is_market_close == False else "🔴 Borsa Kapalı, Son kapanış verisi",
        inline=True
    )
    
    embed.set_footer(text="⚠️ Yatırım tavsiyesi değildir",
                    icon_url=interaction.client.user.display_avatar.url)
    await interaction.followup.send(embed=embed)




# ----- CONSTANTS (put at top of file, next to your other constants) -----
MAX_ALARMS = 3
BAND = 0.30          # +/-30% acceptable target band
UP = "up"
DOWN = "down"
CHECK_INTERVAL_MINUTES = 5

# ----- ALARM FAMILY -----
alarm_group = app_commands.Group(name="alarm", description="Fiyat alarmı yönetimi")
bot.tree.add_command(alarm_group)

# ----- SET ----- 
@alarm_group.command(name="set", description="Bir hisse için fiyat alarmı kurar")
@app_commands.describe(symbol="Stock Symbol", target="Alarmın öteceği fiyat")
async def alarm_set(interaction: discord.Interaction, symbol: str, target: float):
    await interaction.response.defer()

    # 1) Alarm limit check
    current_count = len(get_user_alarms(interaction.user.id))
    if current_count >= MAX_ALARMS:
        await interaction.followup.send(embed=discord.Embed(
            title="⚠️ Alarm sınırı",
            description=(
                f"En fazla {MAX_ALARMS} alarm kurabilirsin "
                f"(şu an {current_count}/{MAX_ALARMS}).\n"
                f"Yeni alarm için `/alarm list` ile birini seç, `/alarm delete` ile kaldır."
            ),
            color=0xf5fc12
        ))
        return

    # 2) Fetch data
    stock = Stock.get_stock(symbol)
    if stock is None:
        await interaction.followup.send(embed=discord.Embed(
            title="⚠️ Veri alınamadı",
            description=f"`{symbol}` için veri çekilemedi. Sembolü kontrol et.",
            color=0xf5fc12
        ))
        return

    current = stock.closing         # verify the real attribute name in data.py

    # 3) Acceptable target band
    lower, upper = current * (1 - BAND), current * (1 + BAND)
    if not (lower <= target <= upper):
        await interaction.followup.send(embed=discord.Embed(
            title="**⚠️ Hedef makul aralık dışında**",
            description=(
                f"**{stock.symbol}** şu an **{current:.2f} TL**.\n"
                f"Hedef {lower:.2f} – {upper:.2f} TL arasında olmalı (±%{BAND * 100:.0f})."
            ),
            color=0xf5fc12
        ))
        return

    # 4) Equality case
    if target == current:
        await interaction.followup.send(embed=discord.Embed(
            title="**⚠️ Anlamsız hedef**",
            description="Hedef mevcut fiyata eşit — beklenecek bir hareket yok :D",
            color=0xf5fc12
        ))
        return

    # 5) Resolve direction once, then persist
    direction = UP if target > current else DOWN
    add_alarm(interaction.user.id, stock.symbol, target, direction)

    ok = discord.Embed(
        title="**🔔 Alarm kuruldu**",
        description=(
            f"**{stock.symbol}** için **{target:.2f} TL** hedefi kaydedildi.\n"
            f"Şu anki fiyat: **{current:.2f} TL** → yön: **{direction}**\n"
            f"Aktif alarm: {current_count + 1}/{MAX_ALARMS}"
        ),
        color=0x04d13b
    )
    ok.set_footer(text="⚠️ Yatırım tavsiyesi değildir")
    await interaction.followup.send(embed=ok)


# ----- LIST ----- 
@alarm_group.command(name="list", description="Kurulu alarmlar listesi")
async def alarm_list(interaction: discord.Interaction):
    await interaction.response.defer()
    user_alarm_list = get_user_alarms(interaction.user.id)

    if not user_alarm_list:
        empty = discord.Embed(
        title="**⚠️Liste bulunamadı**",
        description=(
            f"**{interaction.user.name}** için herhangi bir liste **bulunamadı**.\n"
        ),
        color=0xf5fc12
        )
        
        empty.set_footer(text="⚠️ Yatırım tavsiyesi değildir",
                    icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=empty)
        return
    
    list_info = []
    for alarm_id,symbol, set_value, direction in user_alarm_list:
        if direction == UP:
            direction = "⬆️"
        else:
            direction = "⬇️"

        list_info.append(f"🚨Id : **{alarm_id}** **|** 🏢Hisse : **{symbol}** **|** 💰Hedef Fiyat : **{set_value:.2f}TL** **|** 🚀Hedef Yön : {direction}")
    description = "\n".join(list_info)
    
    embed = discord.Embed(
        title="**📋Alarm Listesi**",
        description=description,
        color=0x04d13b
        )
    
    embed.set_footer(text=f"{len(user_alarm_list)}/{MAX_ALARMS} alarm · Silmek için: /alarm delete <id>",
    icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=embed)


# ----- DELETE ----- 
@alarm_group.command(name="delete", description="Kurulu alarm silme")
@app_commands.describe(alarm_id="Silinecek alarmın id'si")
async def alarm_delete(interaction: discord.Interaction,alarm_id: int):
    await interaction.response.defer()
    
    success = delete_alarm(alarm_id,interaction.user.id)
    
    
    if not success:
        empty = discord.Embed(
        title="**⚠️Alarm Bulunamadı**",
        description=(
            f"**{interaction.user.name}** adlı kullanıcıya ait **{alarm_id}** numaralı id bulunamadı.\n"
        ),
        color=0xf5fc12
        )
        
        empty.set_footer(text="/alarm list ile alarm id'lerini kontrol edin",
                    icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=empty)
        return        
    
    alarm_number = get_user_alarms(interaction.user.id)

    delete = discord.Embed(
        title="**✔️Alarm silindi**",
        description=f"{alarm_id} numaralı alarm başarıyla silinmiştir",
        color=0x04d13b
        )
    
    delete.set_footer(text=f"{len(alarm_number)}/{MAX_ALARMS} alarm · Eklemek için: /alarm set <symbol> <target>",
    icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=delete)

# ---- INDEX ----
@bot.tree.command(name="index", description="BIST endeks değeri")
@app_commands.describe(index="Görüntülenecek endeks")
@app_commands.choices(index=[
    app_commands.Choice(name="BIST 100", value="XU100"),
    app_commands.Choice(name="BIST 30",  value="XU030"),
])
async def index_command(interaction: discord.Interaction, index: app_commands.Choice[str]):
    await interaction.response.defer()

    sonuc = Stock.get_stock(index.value)          # .value = "XU100", .name = "BIST 100"

    if sonuc is None:
        embed_error = discord.Embed(
            title="❌HATA",
            description=f"❔`{index.name}` için veri bulunamadı.",
            color=0xf5fc12
        )
        embed_error.set_footer(icon_url=interaction.client.user.display_avatar.url,
                                text="MarketMind")
        await interaction.followup.send(embed=embed_error)
        return

    # RSI can legitimately be None (flat series) -> format only when it exists
    rsi_text = f"{sonuc.rsi:.2f}" if sonuc.rsi is not None else "veri yok"

    color = rate_to_color(sonuc.changing_rate)

    embed = discord.Embed(
        title=f"📈 {index.name}",
        description=f"""
💰 Değer: {sonuc.closing:,.2f} puan
{rate_to_emoji(sonuc.changing_rate)} Değişim: %{sonuc.changing_rate:.2f}
📊 RSI: {rsi_text}
⚖️ Hacim Oranı: {sonuc.volume_ratio:.2f}x
🗓️ Aylık Değişim: %{sonuc.monthly_rate:.2f}
""",
        color=color
    )

    embed.add_field(
        name="📅 Veri Tarihi",
        value=sonuc.date[:10],
        inline=True
    )

    embed.add_field(
        name="🏦 Borsa Durumu",
        value="🟢 Borsa Açık,⏱️ Piyasa açıkken veriler ~15dk gecikmeli gelir" if sonuc.is_market_close == False else "🔴 Borsa Kapalı, Son kapanış verisi",
        inline=True
    )

    embed.set_footer(text="MarketMind",
                    icon_url=interaction.client.user.display_avatar.url)
    await interaction.followup.send(embed=embed)


# ---- LEARN ----

# Choices are derived from the content dict -> keys can never drift apart
LEARN_CHOICES = []
for key, topic in LEARN_TOPICS.items():
    LEARN_CHOICES.append(app_commands.Choice(name=topic["title"], value=key))
    
    
@bot.tree.command(name="learn", description="Botun kullandığı terimlerin açıklamaları")
@app_commands.describe(topic="Öğrenmek istediğin konu")
@app_commands.choices(topic=LEARN_CHOICES)
async def learn_command(interaction: discord.Interaction, topic: app_commands.Choice[str]):
    content = LEARN_TOPICS[topic.value]
    embed = discord.Embed(
        title=f"📚{content['title']}",
        description=content["text"],
        color=0x3498db
    )
    embed.set_footer(text="MarketMind",icon_url=interaction.client.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ----- COMPARE AI VIEW -----
class CompareView(discord.ui.View):
    def __init__(self, stock_1: Stock, stock_2: Stock, owner_id: int):
        super().__init__(timeout=180)        # 3 min, then the button dies
        self.stock_1 = stock_1               # data carried into the callback
        self.stock_2 = stock_2
        self.owner_id = owner_id
        self.message = None                  # filled in after sending, needed by on_timeout

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Runs before every button in this view. False -> callback never fires."""
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "Bu komutu sen çalıştırmadın. Kendi `/compare` komutunu deneyebilirsin.",
                ephemeral=True                # only that user sees it
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:           # children = every button/select in this view
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="AI Yorumu", emoji="🤖", style=discord.ButtonStyle.primary)
    async def ai_comment(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True                       # single use -> no double token spend
        await interaction.response.edit_message(view=self)   # repaint the stats msg, greyed out

        comment = comment_compare(self.stock_1, self.stock_2)   # ← YOUR function, see below

        if comment is None:
            await interaction.followup.send(embed=discord.Embed(
                title="❌ HATA",
                description="⚠️ Bot yanıt veremedi. Lütfen daha sonra tekrar deneyin.",
                color=0xf5fc12
            ))
            return

        if len(comment) > 4096:
            comment = comment[:4093] + "..."

        embed = discord.Embed(
            title=f"🤖 {self.stock_1.symbol} vs {self.stock_2.symbol} — AI Yorumu",
            description=comment,
            color=0x3498db
        )
        embed.set_footer(text="⚠️ Yatırım tavsiyesi değildir",
                        icon_url=interaction.client.user.display_avatar.url)
        await interaction.followup.send(embed=embed)   # NEW message, stats stays above


# ----- COMPARE -----
@bot.tree.command(name="compare",description="İki hisse verisinin karşılaştırması")
@app_commands.describe(symbol_1="BIST hisse sembolü", symbol_2="BIST hisse sembolü")
async def compare(interaction: discord.Interaction, symbol_1:str , symbol_2:str):
    await interaction.response.defer()
    
    if symbol_1.upper()==symbol_2.upper():
        embed_error = discord.Embed(
            title=f"❌HATA",
            description=f"❔Farklı 2 şirketi karşılaştırabilirsiniz",
            color=0xf5fc12
        )
        
        embed_error.set_footer(icon_url=interaction.client.user.display_avatar.url,
                            text="MarketMind")
        
        await interaction.followup.send(embed=embed_error)
        return 
    
    stock_1 = Stock.get_stock(symbol_1)
    stock_2 = Stock.get_stock(symbol_2)

    if stock_1 is None or stock_2 is None:  
        # Verisi bulunamayan sembolleri topluyoruz
        invalid_symbols = []
        if stock_1 is None:
            invalid_symbols.append(symbol_1.upper())
        if stock_2 is None:
            invalid_symbols.append(symbol_2.upper())

        # Birden fazla sembol hatalıysa "THYAO, GARAN" şeklinde birleştirir
        failed_text = ", ".join(invalid_symbols)

        embed_error = discord.Embed(
            title="❌ HATA",
            description=f"❔ `{failed_text}` için veri bulunamadı. Sembolü kontrol et.",
            color=0xF5FC12
        )
        embed_error.set_footer(
            icon_url=interaction.client.user.display_avatar.url,
            text="MarketMind"
        )
        await interaction.followup.send(embed=embed_error)
        return 
    
    rsi_1 = f"{stock_1.rsi:.2f}" if stock_1.rsi is not None else "veri yok"
    rsi_2 = f"{stock_2.rsi:.2f}" if stock_2.rsi is not None else "veri yok"
    
    embed = discord.Embed(
        title=f"⚖️ {stock_1.symbol} vs {stock_2.symbol}",
        color=0x3498db          # neutral: two stocks may move in opposite directions
    )

    embed.add_field(
        name=f"{rate_to_emoji(stock_1.changing_rate)} {stock_1.symbol}",
        value=(
            f"💰 {stock_1.closing:.2f} TL\n"
            f"📊 Değişim: %{stock_1.changing_rate:.2f}\n"
            f"📈 RSI: {rsi_1}\n"
            f"⚖️ Hacim: {stock_1.volume_ratio:.2f}x\n"
            f"🗓️ Aylık: %{stock_1.monthly_rate:.2f}"
        ),
        inline=True
    )
    
    embed.add_field(
        name=f"{rate_to_emoji(stock_2.changing_rate)} {stock_2.symbol}",
        value=(
            f"💰 {stock_2.closing:.2f} TL\n"
            f"📊 Değişim: %{stock_2.changing_rate:.2f}\n"
            f"📈 RSI: {rsi_2}\n"
            f"⚖️ Hacim: {stock_2.volume_ratio:.2f}x\n"
            f"🗓️ Aylık: %{stock_2.monthly_rate:.2f}"
        ),
        inline=True
    )

    embed.set_footer(text="⚠️ Yatırım tavsiyesi değildir",
                    icon_url=interaction.client.user.display_avatar.url)

    embed.add_field(
        name="🏦 Borsa Durumu",
        value="🟢 Borsa Açık,⏱️ Piyasa açıkken veriler ~15dk gecikmeli gelir" if stock_1.is_market_close == False else f"🔴 Borsa Kapalı, Son kapanış verisi: {stock_1.date[:10]}",
        inline=False
    )
    view = CompareView(stock_1, stock_2, interaction.user.id)
    view.message = await interaction.followup.send(embed=embed, view=view)


# ----- AUTOCOMPLETE -----
@compare.autocomplete("symbol_1")
@compare.autocomplete("symbol_2")
@alarm_set.autocomplete("symbol")
@latest_value.autocomplete("symbol")
@stock_valuation.autocomplete("symbol")
async def symbol_autocomplete(interaction: discord.Interaction,current: str):
    wanted = current.replace("i", "İ").replace("ı", "I").upper()
    matching = []
    
    for code,name in companies.items():
        if wanted in name or wanted in code:
            
            matching.append(
                app_commands.Choice(name=f"{name} ({code})",value=code)
            )
            
    return matching[:7]

# ----- ALARM CHECKER LOOP -----
@tasks.loop(minutes=CHECK_INTERVAL_MINUTES)
async def alarm_checker():
    # Gate 1: market closed -> do nothing, go back to sleep
    if not is_market_open():
        return

    alarms = get_all_alarms()
    if not alarms:
        return
    
    for alarm_id,user_id,symbol,set_value,direction in alarms:
        try:
            stock = Stock.get_stock(symbol)
            
            #Gate 2: data unavailable -> skip this alarm and keep it alive
            if stock is None:
                print(f"[ALARM]{symbol} verisi alınamadı, bu tur atlandı")
                continue
            
            current = stock.closing
            
            triggered = (
                (direction == UP and current >= set_value)
                or (direction == DOWN and current <= set_value)
            )
            if not triggered:
                continue
            
            # Fire: notify, then kill the alarm (single-shot design)
            user = await bot.fetch_user(user_id)
            
            embed = discord.Embed(
                title="🔔 Alarmın öttü!",
                description=(                    
                f"**{symbol}** hedefine ulaştı.\n\n"
                f"🎯 Hedefin: **{set_value:.2f} TL** ({direction})\n"
                f"💰 Güncel fiyat: **{current:.2f} TL**"
                ),
                color=0x04d13b
                )
            
            embed.set_footer(text="⚠️ Yatırım tavsiyesi değildir")
            
            await user.send(embed=embed)
            delete_alarm(alarm_id,user_id)
            print(f"[ALARM] #{alarm_id} tetiklendi ve silindi ({symbol} @ {current:.2f}) ")
            
        except discord.Forbidden:
            # User's DMs are closed. Keep the alarm, it may work later.
            print(f"[ALARM] #{alarm_id}: kullanıcı DM'e kapalı,alarm korundu")
        
        except Exception as e:
            # One bad alarm must never kill the whole loop
            print(f"[ALARM] #{alarm_id} kontrolünde hata: {type(e).__name__} - {e}")

@alarm_checker.before_loop
async def before_alarm_checker():
    # Don't run the first iteration before the bot is connected
    await bot.wait_until_ready()
                
bot.run(TOKEN)  #botu baslat ve Discord'a baglan (en sonda olmali)
