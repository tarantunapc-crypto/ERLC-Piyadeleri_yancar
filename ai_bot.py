import os
import discord
from discord.ext import commands
from google import genai
import asyncio

from config import TOKEN

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    ai_client = None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

def build_system_prompt(user: discord.Member) -> str:
    roles = [r.id for r in user.roles]
    is_unregistered = len(roles) == 1 or 1542271426386591894 in roles
    is_banned = 1534715583826759790 in roles
    is_management = any(rid in roles for rid in [1529546007635824680, 1539167256246747186, 1534798061845483694, 1537934087166369812])

    prompt = """Sen ERLC Piyadeleri Discord sunucusu için geliştirilmiş bir Yapay Zeka (AI) destek botusun. Sadece bilet (ticket) kanallarında çalışırsın. Amacın bilet açan üyelere 1 defaya mahsus yardımcı olmak. Saygılı ve profesyonel bir dil kullan.

ÖNEMLİ KURAL:
Eğer kullanıcıya hiçbir şekilde yardımcı olamayacağını düşünüyorsan SADECE ŞU KELİMEYİ YAZ: YÖNETİM_ETİKETLE
Ancak kullanıcının erişim engeli varsa bunu ona açıkla, yönetimi etiketleme. Sadece çaresiz kaldığında YÖNETİM_ETİKETLE yaz.

SUNUCU KANALLARI:
- Kurallar (<#1532828330380890452>)
- Duyuru (<#1541355760829726760>)
- Uyarılar (<#1532828434739368149>)
- Sohbet Kanalı (<#1532828722158112779>)
- Ticket Kanalı (<#1534770099179884564>)
- Kayıt Kanalı (<#1532831582753128530>)
- Yardım Bekleme (<#1532829788824404274>)
- Sosyal Medya (<#1532828546865696889>)
- Sınırlı Erişim (<#1532828892404912148>)
"""

    if is_unregistered:
        prompt += "\nKURAL: Bu kullanıcı KAYITSIZ. Sadece Kayıt, Bilet, Yardım Bekleme, Kurallar ve Sosyal Medya hakkında bilgi ver. Diğerlerini sorarsa kayıt olması gerektiğini söyle."
    elif is_banned:
        prompt += "\nKURAL: Bu kullanıcı YASAKLI. Sadece Bilet, Yardım Bekleme, Kurallar ve Sınırlı Erişim hakkında bilgi ver. Etkinlik veya sohbet sorarsa Sınırlı Erişimden yetkililere ulaşmasını söyle."
    elif is_management:
        prompt += "\nKURAL: Bu kullanıcı YÖNETİM. Teknik sorularına detaylı cevap ver."
    
    return prompt

def generate_ai_response(prompt: str) -> str:
    if not ai_client: return "YÖNETİM_ETİKETLE"
    try:
        response = ai_client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Hatası: {e}")
        return "YÖNETİM_ETİKETLE" 

@bot.event
async def on_ready():
    print(f"Yapay Zeka Bilet Botu {bot.user} olarak giriş yaptı!")

@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, discord.TextChannel) and channel.name.startswith("ticket-"):
        await asyncio.sleep(4)
        topic = channel.topic or ""
        if "acan_id:" in topic:
            try:
                user_id = int(topic.split("acan_id:")[1].strip())
                user = channel.guild.get_member(user_id)
                if user:
                    await channel.send(f"[ {user.mention} Merhabalar, size nasıl yardımcı olabiliriz? Sorununuzu detaylıca yazarsanız sevinirim. ]")
            except Exception as e:
                pass

@bot.event
async def on_message(message):
    if message.author.bot: return
    if isinstance(message.channel, discord.TextChannel) and message.channel.name.startswith("ticket-"):
        has_replied = False
        async for msg in message.channel.history(limit=50):
            if msg.author == bot.user and "size nasıl yardımcı olabiliriz?" not in msg.content:
                has_replied = True
                break
                
        if has_replied: return

        async with message.channel.typing():
            messages = []
            async for msg in message.channel.history(limit=15): messages.append(msg)
            messages.reverse()
            
            conversation_text = ""
            for msg in messages:
                if msg.author.bot:
                    if "destek talebi" not in msg.content.lower() and "nasıl yardımcı olabiliriz" not in msg.content.lower():
                        conversation_text += f"Bot: {msg.content}\n"
                else:
                    conversation_text += f"{msg.author.display_name}: {msg.content}\n"
            
            system_prompt = build_system_prompt(message.author)
            prompt = f"{system_prompt}\n\n--- KONUŞMA GEÇMİŞİ ---\n{conversation_text}\nAI:"
            
            response_text = await asyncio.to_thread(generate_ai_response, prompt)
            
            if "YÖNETİM_ETİKETLE" in response_text or "YONETIM_ETIKETLE" in response_text:
                await message.channel.send(f"Bu konuda size daha detaylı ve doğru yardımcı olabilmek için yönetim ekibimizi konuya dahil ediyorum.\n<@&1529546007635824680> <@&1539167256246747186> <@&1534798061845483694> <@&1537934087166369812>")
            else:
                if len(response_text) > 1950:
                    for chunk in [response_text[i:i+1950] for i in range(0, len(response_text), 1950)]: await message.channel.send(chunk)
                else:
                    await message.channel.send(response_text)

if __name__ == "__main__":
    bot.run(TOKEN)
