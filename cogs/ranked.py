import discord, asyncio, random
from discord.ext import commands
from config import MIN_WAGER

RANKS = {
    "Beginner": (0, "🌱"),
    "Poké Trainer": (100, "🎓"),
    "Gym Leader": (300, "💪"),
    "Elite Four": (600, "⭐"),
    "Champion": (1000, "👑"),
    "Master": (1500, "🔮"),
    "Legend": (2500, "🌟")
}

def get_rank(score):
    current = "Beginner"
    for name, (min_score, _) in RANKS.items():
        if score >= min_score:
            current = name
    return current

class Ranked(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command()
    async def rduel(self, ctx, opponent: discord.Member, wager: int):
        if wager < MIN_WAGER: return await ctx.send(f"Aposta mínima: {MIN_WAGER}🪙")
        # Verificação de saldo, criação de batalha, etc.
        await ctx.send("Sistema ranqueado em construção. Use !queue para matchmaking.")

    @commands.command()
    async def queue(self, ctx, wager: int = 100):
        await ctx.send("Entrou na fila! Aguardando oponente...")

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        if not member: member = ctx.author
        async with self.bot.db.execute("SELECT score, wins, losses, best_streak FROM player_ranks WHERE user_id=?", (member.id,)) as cur:
            row = await cur.fetchone()
        if not row:
            return await ctx.send("Nenhum dado ranqueado ainda.")
        score, wins, losses, best = row
        rank = get_rank(score)
        embed = discord.Embed(title=f"📊 Perfil de {member.display_name}")
        embed.add_field(name="Rank", value=f"{RANKS[rank][1]} {rank}", inline=True)
        embed.add_field(name="Score", value=score, inline=True)
        embed.add_field(name="Vitórias/Derrotas", value=f"{wins}/{losses}", inline=True)
        embed.add_field(name="Melhor Sequência", value=best, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def lb(self, ctx):
        async with self.bot.db.execute("SELECT user_id, score FROM player_ranks ORDER BY score DESC LIMIT 10") as cur:
            rows = await cur.fetchall()
        embed = discord.Embed(title="🏆 Leaderboard")
        for i, (uid, score) in enumerate(rows, 1):
            member = ctx.guild.get_member(uid)
            name = member.display_name if member else "Usuário Desconhecido"
            embed.add_field(name=f"#{i} {name}", value=f"Score: {score}", inline=False)
        await ctx.send(embed=embed)
        