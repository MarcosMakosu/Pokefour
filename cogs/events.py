import discord, asyncio, json
from discord.ext import commands
from models import load_base_stats

TMS = [
    {"number": 1, "name": "TM01 - Focus Punch", "move_id": 264, "price": 3000},
    {"number": 2, "name": "TM02 - Dragon Claw", "move_id": 337, "price": 4000},
    # Adicione mais
]

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tm(self, ctx, tm_number: int, pokemon_id: int):
        tm_name = f"tm{tm_number:02d}"
        # Verifica se o usuário tem a TM no inventário
        async with self.bot.db.execute("SELECT quantity FROM inventory WHERE user_id=? AND item_name=?", (ctx.author.id, tm_name)) as cur:
            inv = await cur.fetchone()
        if not inv or inv[0] <= 0: return await ctx.send("Você não tem essa TM.")
        # Verifica Pokémon
        async with self.bot.db.execute("SELECT * FROM user_pokemon WHERE id=? AND user_id=?", (pokemon_id, ctx.author.id)) as cur:
            poke = await cur.fetchone()
        if not poke: return await ctx.send("Pokémon não encontrado.")
        # Busca dados da TM
        tm = next((t for t in TMS if t["number"] == tm_number), None)
        if not tm: return await ctx.send("TM inválida.")
        # Substitui o primeiro golpe (simplificado)
        moves = json.loads(poke[14])
        moves[0] = tm["move_id"]
        await self.bot.db.execute("UPDATE user_pokemon SET moves=? WHERE id=?", (json.dumps(moves), pokemon_id))
        await self.bot.db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE user_id=? AND item_name=?",
                                  (ctx.author.id, tm_name))
        await self.bot.db.commit()
        await ctx.send(f"📀 {poke[3] or 'Pokémon'} aprendeu {tm['name']}!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def startevent(self, ctx, event_type: str):
        # Exemplo: double score, spawn lendário, etc.
        await ctx.send(f"Evento '{event_type}' iniciado! (implementação futura)")