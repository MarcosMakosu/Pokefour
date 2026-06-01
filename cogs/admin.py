import discord
from discord.ext import commands
from config import ADMIN_ROLE_ID

def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or discord.utils.get(ctx.author.roles, id=ADMIN_ROLE_ID)
    return commands.check(predicate)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_admin()
    async def editpokemon(self, ctx, user: discord.Member, pokemon_id: int, field: str, *, value: str):
        allowed = ["level", "iv_hp", "iv_atk", "iv_def", "iv_spatk", "iv_spdef", "iv_speed", "shiny", "species_id", "moves", "current_hp"]
        if field not in allowed: return await ctx.send(f"Campos permitidos: {', '.join(allowed)}")
        if field in ["level", "iv_hp", "iv_atk", "iv_def", "iv_spatk", "iv_spdef", "iv_speed", "shiny", "species_id", "current_hp"]:
            value = int(value)
        async with self.bot.db.execute("SELECT user_id FROM user_pokemon WHERE id=?", (pokemon_id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] != user.id: return await ctx.send("Pokémon não pertence a esse usuário.")
        await self.bot.db.execute(f"UPDATE user_pokemon SET {field}=? WHERE id=?", (value, pokemon_id))
        await self.bot.db.commit()
        await ctx.send(f"✅ Pokémon {pokemon_id} atualizado: `{field}` = `{value}`")

    @commands.command()
    @is_admin()
    async def giveitem(self, ctx, user: discord.Member, item_name: str, quantity: int = 1):
        await self.bot.db.execute(
            "INSERT INTO inventory (user_id, item_name, quantity) VALUES (?,?,?) ON CONFLICT(user_id, item_name) DO UPDATE SET quantity = quantity + ?",
            (user.id, item_name, quantity, quantity))
        await self.bot.db.commit()
        await ctx.send(f"🎁 {quantity}x {item_name} dado a {user.display_name}")

    @commands.command()
    @is_admin()
    async def takeitem(self, ctx, user: discord.Member, item_name: str, quantity: int = 1):
        await self.bot.db.execute("UPDATE inventory SET quantity = MAX(0, quantity - ?) WHERE user_id=? AND item_name=?",
                                  (quantity, user.id, item_name))
        await self.bot.db.commit()
        await ctx.send(f"❌ {quantity}x {item_name} removido de {user.display_name}")

    @commands.command()
    @is_admin()
    async def setmoney(self, ctx, user: discord.Member, amount: int):
        await self.bot.db.execute("UPDATE player_economy SET pokedollars=? WHERE user_id=?", (amount, user.id))
        await self.bot.db.commit()
        await ctx.send(f"💰 Saldo de {user.display_name} definido para {amount}🪙")

    @commands.command()
    @is_admin()
    async def setrank(self, ctx, user: discord.Member, score: int):
        await self.bot.db.execute("INSERT OR REPLACE INTO player_ranks (user_id, score) VALUES (?,?)", (user.id, score))
        await self.bot.db.commit()
        await ctx.send(f"📊 Score de {user.display_name} alterado para {score}")