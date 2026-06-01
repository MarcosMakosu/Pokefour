import discord, asyncio, random
from discord.ext import commands
from models import load_base_stats, calc_hp, calc_other_stat

class Stadium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stadium(self, ctx):
        channel_id = ctx.channel.id
        async with self.bot.db.execute("SELECT * FROM stadiums WHERE channel_id=?", (channel_id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return await ctx.send("Este canal não é um estádio. Peça a um admin para criar um.")
        if row[1] is None:  # Bot defende
            await ctx.send("🤖 O líder é um treinador misterioso! Batalha 3v3 em breve.")
        else:
            owner = ctx.guild.get_member(row[1])
            await ctx.send(f"Estádio defendido por {owner.display_name}. Use !stadium para desafiar.")