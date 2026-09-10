import os
import discord
from discord.ext import commands
from google import genai
import asyncio

# config.py icinden TOKEN al
from config import TOKEN

# Gemini API Yapılandırması
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    ai_client = None
    print("UYARI: GEMINI_API_KEY ortam değişkeni bulunamadı. Yapay zeka cevap veremeyebilir!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

def build_system_prompt(user: discord.Member) -> str:
    roles = [r.id for r in user.roles]
    
    # Eger kullanıcının sadece @everyone rolü varsa (len == 1) veya Kayıtsız rolü varsa
    is_unregistered = len(roles) == 1 or 1542271426386591894 in roles
    is_banned = 1534715583826759790 in roles
    is_management = any(rid in roles for rid in [1529546007635824680, 1539167256246747186, 1534798061845483694, 1537934087166369812])

    prompt = """Sen ERLC Piyadeleri Discord sunucusu için geliştirilmiş bir Yapay Zeka (AI) destek botusun.
Sadece bilet (ticket) kanallarında çalışırsın. Amacın bilet açan üyelere 1 defaya mahsus yardımcı olmak, sorularına yanıt verip çözüm üretmektir.
Kurallar ve içerik dışında bir şey uydurmamaya özen göster. Samimi, saygılı ve profesyonel bir dil kullan.

ÖNEMLİ KURAL:
Eğer sorulan soru senin bilmediğin bir şeyse, sistemde karşılığı yoksa veya gerçekten kullanıcıya hiçbir şekilde yardımcı olamayacağını düşünüyorsan SADECE VE SADECE ŞU KELİMEYİ YAZ:
YÖNETİM_ETİKETLE
Bu kelimeyi yazarsan sistem otomatik olarak gerçek yetkilileri çağıracaktır. Ancak eğer kullanıcının sorduğu soruya bir cevabın varsa VEYA kullanıcının erişim engeli/kayıtsızlık durumu yüzünden işlemi yapamıyorsa bunu kullanıcıya güzelce AÇIKLA (Yönetimi etiketleme). Sadece gerçekten çaresiz kaldığın durumlarda YÖNETİM_ETİKETLE yaz.

SUNUCU GENEL KANALLARI:
- Kurallar Kanalı (<#1532828330380890452>): Sunucu kuralları yazar. (Kural İlkeleri: https://canva.link/ma7hw7a6ex9lmmw)
- Duyuru Kanalı (<#1541355760829726760>): Sunucu içi gelişmeler ve duyurular.
- Uyarılar Kanalı (<#1532828434739368149>): Üyelerin uyarı seviyeleri ve yetkililer tarafından gönderilen gerekçeler.
- ER:LC Duyuru Kanalı (<#1541354459408629830>): Emergency Response: Liberty County oyun duyuruları. (Oyun: https://www.roblox.com/tr/games/2534724415/Emergency-Response-Liberty-County)
- Sosyal Medya Kanalı (<#1532828546865696889>): Instagram (https://www.instagram.com/erlcpiyadeleri/) ve Youtube (https://www.youtube.com/@RPservers-Privateservers).
- Reklam Kanalı (<#1532828574028140564>): Başka sunucuların reklamları.
- İstek-Öneri Kanalı (<#1545562405076209714>): Eklenti/özellik istekleri. Yetkililer inceler, kabul ederse ekler, reddederse siler.
- Sohbet Kanalı (<#1532828722158112779>): Üyelerin sohbet kanalı. Orada sohbet edip aktif olunabilir.
- Medya Kanalı (<#1532829033564213298>): Oyun/aktivite fotoğrafları ve linkleri paylaşılır. (Metin yazmak yasaktır)
- Perm Al Kanalı (<#1532829702274682890>): "Driver", "Pvp", "Builder", "Legal", "İllegal", "Sıcak Kanlı" rolleri alınabilir. Legal ve İllegal aynı anda alınamaz.
- Play Music Kanalı (<#1532828810582429907>): Ses kanalındayken müzik oynatma.
- Bot Komut Kanalı (<#1544809399296589885>): Market sistemi vb. etkileşimler (market.py).
- Yaşanan Olaylar Kanalı (<#1544760160042356828>): Olay günlükleri.
- Etkinlik Sahne Kanalı (<#1547268189136617554>): Toplum etkinlikleri.
- Anlık Haber Kanalı (<#1532829077885554809>): Oyun içi kurgu haberler.
- VS Talep Kanalı (<#1537136926287593503>): Yarış/kapışma talepleri. GÜNDEM kategorisinde kanal açılır, sonuçlar VS Sonuç kanalına atılır.
- Ses Kanalları (SALON 1 <#1532829368068472913>, SALON 2 <#1540081816013111296>, BİREBİR <#1532829412058202203>): Girenlere "Aktif" rolü verilir.
- AFK Ses Kanalı (<#1532829520627765378>): Girenler sessize alınır ve "AFK" rolü verilir.
- Kayıt Kanalı (<#1532831582753128530>): Sadece rolsüzler görebilir. Kayıt olarak diğer kanallara erişim sağlanır.
- Sınırlı Erişim Kanalı (<#1532828892404912148>): "Yasaklı" üyeler görebilir ve yetkililere kendilerini açıklayabilirler.
- Ticket Kanalı (<#1534770099179884564>): Destek talebi oluşturma kanalı.
- Yardım Bekleme Ses Kanalı (<#1532829788824404274>): Yetkililerden sesli destek alma kanalı.
"""

    if is_unregistered:
        prompt += """
---
DİKKAT KULLANICI DURUMU: KAYITSIZ (VEYA ROLSÜZ)
KURAL: Bilet açan bu kullanıcı henüz KAYITSIZ. Bu kullanıcıya SADECE Kayıt Kanalı, Bilet Kanalı, Yardım Bekleme Ses Kanalı, Kurallar Kanalı ve Sosyal Medya Kanalı hakkında bilgi verebilirsin. 
Diğer hiçbir kanal hakkında bilgi VEREMEZSİN. Eğer sohbet, medya, aktiflik gibi diğer kanalları sorarsa: "Henüz kayıtlı olmadığınız için o kanallara erişiminiz yok, lütfen Kayıt Kanalı'ndan kayıt işlemlerinizi tamamlayın" gibi bir cevap ver. Sakın YÖNETİM_ETİKETLE yazma, durumu ona kendin izah et.
"""
    elif is_banned:
        prompt += """
---
DİKKAT KULLANICI DURUMU: YASAKLI
KURAL: Bilet açan bu kullanıcı YASAKLI durumunda.
Bu kullanıcıya SADECE Bilet Kanalı, Yardım Bekleme Ses Kanalı, Kurallar Kanalı ve Sınırlı Erişim Kanalı hakkında bilgi verebilirsin. 
Yasaklı olduğu için sohbet veya diğer etkinliklere katılamaz. Bunu sorarsa durumunu Sınırlı Erişim kanalından yetkililerle görüşmesi gerektiğini nazikçe belirt.
"""
    elif is_management:
        try:
            with open("uyari_sistemi.py", "r", encoding="utf-8") as f: uyari_code = f.read()
        except Exception: uyari_code = "Dosya bulunamadı veya okunamadı."
        
        try:
            with open("registration.py", "r", encoding="utf-8") as f: reg_code = f.read()
        except Exception: reg_code = "Dosya bulunamadı veya okunamadı."
        
        try:
            with open("yardim_bekleme.py", "r", encoding="utf-8") as f: yardim_code = f.read()
        except Exception: yardim_code = "Dosya bulunamadı veya okunamadı."

        prompt += f"""
---
DİKKAT KULLANICI DURUMU: YÖNETİM EKİBİ (YETKİLİ)
Bilet açan kullanıcı yönetim ekibinden biridir. Normal konulardaki sorularına detaylı cevap ver.
Eğer sadece yetkililerin görebildiği kanallar veya bu kanalların arka planında çalışan sistemler/dosyalarla (uyari_sistemi.py, registration.py, yardim_bekleme.py) ilgili teknik soru sorarsa, aşağıdaki dosyaların içeriğini inceleyerek kodların nasıl çalıştığını anlat:

-- Yetkili Özel Kanalları --
- Only-Moderatör Kanalı (<#1532828404347437287>): Yetkililerin işlemlerinin gösterildiği log kanalı.
- Uyarı Panel (<#1547188376778579988>): uyari_sistemi.py dosyasıyla çalışan uyarı panel kanalı.
- Onay-Red Kanalı (<#1532828473972752555>): Kayıt başvurularının düştüğü kanal (registration.py).
- Önemli Log Bildirim Kanalı (<#1532829734742786168>): Yardım Bekleme ses kanalına girenlerin logunun düştüğü kanal (yardim_bekleme.py).

-- uyari_sistemi.py İçeriği --
```python
{uyari_code}
```
-- registration.py İçeriği --
```python
{reg_code}
```
-- yardim_bekleme.py İçeriği --
```python
{yardim_code}
```
"""
    
    return prompt

def generate_ai_response(prompt: str) -> str:
    if not ai_client:
        return "⚠️ Hata: GEMINI_API_KEY ortam değişkeni ayarlanmamış! (Railway'den Variables kısmına eklemelisin)"
    try:
        response = ai_client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Hatası: {e}")
        return "YÖNETİM_ETİKETLE" 

@bot.event
async def on_ready():
    print(f"Yapay Zeka Bilet Botu {bot.user} olarak giriş yaptı ve biletleri dinlemeye hazır!")

@bot.event
async def on_guild_channel_create(channel):
    # Yeni bir bilet kanalı oluşturulduğunda ilk mesajı gönder
    if isinstance(channel, discord.TextChannel) and channel.name.startswith("ticket-"):
        await asyncio.sleep(4)
        
        topic = channel.topic or ""
        if "acan_id:" in topic:
            try:
                user_id = int(topic.split("acan_id:")[1].strip())
                user = channel.guild.get_member(user_id)
                if user:
                    # Başlangıç Karşılama Mesajı
                    await channel.send(f"[ {user.mention} Merhabalar, size nasıl yardımcı olabiliriz? Sorununuzu veya sorunuzu detaylıca yazarsanız sevinirim. ]")
            except Exception as e:
                print("Karşılama mesajı gönderilirken hata:", e)

@bot.event
async def on_message(message):
    # Botların kendi mesajlarına yanıt vermesini engelle
    if message.author.bot:
        return
    
    if isinstance(message.channel, discord.TextChannel) and message.channel.name.startswith("ticket-"):
        
        # --- TEK CEVAP KONTROLÜ ---
        # Bot daha önce bu kanalda yapay zeka ile cevap vermiş mi kontrol et.
        # Eğer botun attığı mesajlar içinde "size nasıl yardımcı olabiliriz?" içermeyen bir mesaj varsa, demek ki cevap verilmiş.
        has_replied = False
        async for msg in message.channel.history(limit=50):
            if msg.author == bot.user and "size nasıl yardımcı olabiliriz?" not in msg.content:
                has_replied = True
                break
                
        if has_replied:
            # Yapay zeka zaten 1 defa asıl cevabı vermiş, bu yüzden bir daha karışmıyor.
            return
        # ---------------------------

        async with message.channel.typing():
            messages = []
            async for msg in message.channel.history(limit=15):
                messages.append(msg)
            
            messages.reverse()
            
            conversation_text = ""
            for msg in messages:
                if msg.author.bot:
                    if msg.content and "destek talebi oluşturdu" not in msg.content.lower() and "size nasıl yardımcı olabiliriz" not in msg.content.lower():
                        conversation_text += f"Bot: {msg.content}\n"
                else:
                    conversation_text += f"{msg.author.display_name}: {msg.content}\n"
            
            system_prompt = build_system_prompt(message.author)
            prompt = f"{system_prompt}\n\n--- KONUŞMA GEÇMİŞİ ---\n{conversation_text}\nAI:"
            
            response_text = await asyncio.to_thread(generate_ai_response, prompt)
            
            if "YÖNETİM_ETİKETLE" in response_text or "YONETIM_ETIKETLE" in response_text:
                await message.channel.send(
                    f"Bu konuda size daha detaylı ve doğru yardımcı olabilmek için yönetim ekibimizi konuya dahil ediyorum.\n"
                    f"<@&1529546007635824680> <@&1539167256246747186> <@&1534798061845483694> <@&1537934087166369812>"
                )
            else:
                if len(response_text) > 1950:
                    for chunk in [response_text[i:i+1950] for i in range(0, len(response_text), 1950)]:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response_text)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("HATA: TOKEN bulunamadı. Lütfen config.py içerisindeki TOKEN ayarını kontrol edin ve ayarlayın.")
