import discord
from discord.ext import commands
from flask import Flask
import threading
import os
import asyncio
import datetime
from collections import defaultdict

# ===== سيرفر وهمي عشان Render ما يطفي البوت =====
app = Flask('')
@app.route('/')
def home(): return "البوت شغال!"
def run(): app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run).start()

# ===== هون عدل على كيفك =====
PREFIX = "!"
WELCOME_CHANNEL_ID = 0  # حط ايدي روم الترحيب، اذا خليته 0 بيرحب بأول روم
# =============================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)
msg_count = defaultdict(list)

@bot.event
async def on_ready():
    print(f"اشتغل! {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Los Santos | !مساعدة"))

# ===== 1. ترحيب فخم =====
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is None and len(member.guild.text_channels) > 0:
        channel = member.guild.text_channels[0]
    if channel:
        embed = discord.Embed(
            title=f"🔥 اهلا وسهلا {member.name} 🔥",
            description=f"نورت سيرفر **{member.guild.name}** 👑\n\nانت العضو رقم **{member.guild.member_count}**\n\nاقرا القوانين واستمتع معنا ❤️",
            color=0xFFD700
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url="https://i.imgur.com/2nCt3Sbl.jpg")
        embed.set_footer(text=f"LS BOT | {member.guild.name}")
        await channel.send(f"{member.mention}", embed=embed)

# ===== 4. حماية =====
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    # منع روابط
    if "discord.gg/" in message.content or "discord.com/invite/" in message.content:
        if not message.author.guild_permissions.administrator:
            await message.delete()
            await message.channel.send(f"{message.author.mention} ممنوع تنشر روابط! ⚠️", delete_after=5)
            return
    # منع سبام
    now = datetime.datetime.now()
    msg_count[message.author.id].append(now)
    msg_count[message.author.id] = [t for t in msg_count[message.author.id] if (now - t).total_seconds() < 5]
    if len(msg_count[message.author.id]) > 5:
        await message.channel.send(f"{message.author.mention} خفف شوي لا تسبم! ⛔", delete_after=5)
        try: await message.author.timeout(datetime.timedelta(minutes=1), reason="سبام")
        except: pass
        msg_count[message.author.id] = []
        return
    await bot.process_commands(message)

# ===== مساعدة =====
@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🔥 اوامر LS BOT 🔥", color=0xFFD700)
    embed.add_field(name="!اعطي @شخص @رتبة", value="يعطي رتبة", inline=False)
    embed.add_field(name="!شيل @شخص @رتبة", value="يشيل رتبة", inline=False)
    embed.add_field(name="!تكت", value="يفتح تكت خاص", inline=False)
    embed.add_field(name="!سكر", value="يسكر التكت", inline=False)
    embed.add_field(name="!قفل / !افتح", value="قفل وفتح الروم", inline=False)
    await ctx.send(embed=embed)

# ===== 3. اعطاء رتبة =====
@bot.command(name="اعطي")
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    embed = discord.Embed(title="✅ تم اعطاء رتبة", description=f"{member.mention} اخذ رتبة {role.mention}\nمن: {ctx.author.mention}", color=0x00FF00)
    await ctx.send(embed=embed)

@bot.command(name="شيل")
@commands.has_permissions(manage_roles=True)
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"✅ تم شيل {role.mention} من {member.mention}")

# ===== 2. تكت فخم =====
@bot.command(name="تكت")
async def ticket(ctx):
    guild = ctx.guild
    for ch in guild.text_channels:
        if ch.name == f"تكت-{ctx.author.name.lower()}":
            await ctx.send(f"عندك تكت مفتوح اصلا {ch.mention}")
            return
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    for role in guild.roles:
        if role.permissions.administrator:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    channel = await guild.create_text_channel(f"تكت-{ctx.author.name}", overwrites=overwrites)
    embed = discord.Embed(title="🎫 تم فتح تكتك", description=f"{ctx.author.mention} اهلا فيك\nاكتب مشكلتك ورح يرد عليك الادمن\nعشان تسكر اكتب `!سكر`", color=0x00BFFF)
    await ctx.send(f"تم فتح تكتك {channel.mention} ✅")
    await channel.send(embed=embed)

@bot.command(name="سكر")
@commands.has_permissions(manage_channels=True)
async def close_ticket(ctx):
    if "تكت-" in ctx.channel.name:
        await ctx.send("رح يتسكر التكت بعد 5 ثواني...")
        await asyncio.sleep(5)
        await ctx.channel.delete()
    else:
        await ctx.send("هاد مو روم تكت!")

@bot.command(name="قفل")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل الروم")

@bot.command(name="افتح")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح الروم")

TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
