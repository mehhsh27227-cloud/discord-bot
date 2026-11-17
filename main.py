import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is Online!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! البوت شغال!")

@bot.command()
async def hello(ctx):
    await ctx.send(f"اهلا {ctx.author.mention}")

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)

