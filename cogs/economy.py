import discord, asyncio, json
from discord.ext import commands
from datetime import datetime, timedelta
from config import DAILY_BASE, DAILY_STREAK_BONUS
from models import calc_hp  # Usado no comando 'use'

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def daily(self, ctx):
        now = datetime.utcnow()
        async with self.bot.db.execute("SELECT pokedollars, last_daily, streak FROM player_economy WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        if not row:
            await self.bot.db.execute("INSERT INTO player_economy (user_id, pokedollars) VALUES (?,0)", (ctx.author.id,))
            row = (0, None, 0)
        coins, last, streak = row
        if last:
            last = datetime.fromisoformat(last)
            if now - last < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last)
                return await ctx.send(f"⏰ Volte em {remaining.seconds//3600}h {(remaining.seconds%3600)//60}min.")
            streak = streak + 1 if now - last < timedelta(hours=48) else 1
        else:
            streak = 1
        bonus = min(streak * DAILY_STREAK_BONUS, 500)
        total = DAILY_BASE + bonus
        await self.bot.db.execute(
            "UPDATE player_economy SET pokedollars = pokedollars + ?, last_daily=?, streak=?, total_claimed=total_claimed+1 WHERE user_id=?",
            (total, now.isoformat(), streak, ctx.author.id))
        await self.bot.db.commit()
        await ctx.send(f"💰 Coletou {total} moedas! Streak: {streak} dia(s)")

    @commands.command(aliases=["money"])
    async def balance(self, ctx):
        async with self.bot.db.execute("SELECT pokedollars FROM player_economy WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        coins = row[0] if row else 0
        await ctx.send(f"🪙 Saldo: {coins} PokéDólares")

    @commands.command()
    async def shop(self, ctx):
        async with self.bot.db.execute("SELECT item_name, price, emoji, description FROM shop_items") as cur:
            items = await cur.fetchall()
        embed = discord.Embed(title="🏪 PokéShop")
        for name, price, emoji, desc in items:
            embed.add_field(name=f"{emoji} {name} – {price}🪙", value=desc, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def buy(self, ctx, *, query: str):
        parts = query.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].isdigit():
            item_name, qty = parts[0].lower(), int(parts[1])
        else:
            item_name, qty = query.lower(), 1
        async with self.bot.db.execute("SELECT price, stock FROM shop_items WHERE item_name=?", (item_name,)) as cur:
            item = await cur.fetchone()
        if not item: return await ctx.send("Item não encontrado.")
        price, stock = item
        if stock >= 0 and qty > stock: return await ctx.send("Estoque insuficiente.")
        total = price * qty
        async with self.bot.db.execute("SELECT pokedollars FROM player_economy WHERE user_id=?", (ctx.author.id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < total: return await ctx.send("Saldo insuficiente.")
        await self.bot.db.execute("UPDATE player_economy SET pokedollars = pokedollars - ? WHERE user_id=?",
                                  (total, ctx.author.id))
        await self.bot.db.execute(
            "INSERT INTO inventory (user_id, item_name, quantity) VALUES (?,?,?) ON CONFLICT(user_id, item_name) DO UPDATE SET quantity = quantity + ?",
            (ctx.author.id, item_name, qty, qty))
        if stock > 0:
            await self.bot.db.execute("UPDATE shop_items SET stock = stock - ? WHERE item_name=?", (qty, item_name))
        await self.bot.db.commit()
        await ctx.send(f"✅ {qty}x {item_name} comprado(s) por {total}🪙")

    @commands.command()
    async def bag(self, ctx):
        async with self.bot.db.execute("SELECT item_name, quantity FROM inventory WHERE user_id=?", (ctx.author.id,)) as cur:
            items = await cur.fetchall()
        if not items: return await ctx.send("Mochila vazia.")
        msg = "\n".join([f"{name}: {qty}" for name, qty in items])
        await ctx.send(f"🎒 Mochila:\n{msg}")

    @commands.command()
    async def use(self, ctx, *, args: str):
        parts = args.split(" ", 1)
        if len(parts) < 2:
            return await ctx.send("Uso: `!use <item> <pokemon_id ou nickname>`")
        item_name = parts[0].lower()
        target = parts[1]
        async with self.bot.db.execute("SELECT quantity FROM inventory WHERE user_id=? AND item_name=?", (ctx.author.id, item_name)) as cur:
            inv = await cur.fetchone()
        if not inv or inv[0] <= 0: return await ctx.send("Você não possui esse item.")
        async with self.bot.db.execute("SELECT effect_type, effect_value FROM shop_items WHERE item_name=?", (item_name,)) as cur:
            shop = await cur.fetchone()
        if not shop: return await ctx.send("Item inválido.")
        effect_type, effect_json = shop
        effect = json.loads(effect_json)
        try:
            poke_id = int(target)
            async with self.bot.db.execute("SELECT * FROM user_pokemon WHERE id=? AND user_id=?", (poke_id, ctx.author.id)) as cur:
                poke = await cur.fetchone()
        except ValueError:
            async with self.bot.db.execute("SELECT * FROM user_pokemon WHERE nickname=? AND user_id=?", (target, ctx.author.id)) as cur:
                poke = await cur.fetchone()
        if not poke: return await ctx.send("Pokémon não encontrado.")
        if effect_type == "heal":
            hp_restore = effect["hp_restore"]
            # Calcular max_hp (precisa dos base stats)
            species_data = await load_base_stats(poke[2])  # species_id está no índice 2
            max_hp = calc_hp(species_data["stats"]["hp"], poke[5], poke[4])  # iv_hp=5, level=4
            current = poke[13]
            if hp_restore == "full":
                new_hp = max_hp
            else:
                new_hp = min(max_hp, current + int(hp_restore))
            await self.bot.db.execute("UPDATE user_pokemon SET current_hp=? WHERE id=?", (new_hp, poke[0]))
            await self.bot.db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE user_id=? AND item_name=?",
                                      (ctx.author.id, item_name))
            await self.bot.db.commit()
            await ctx.send(f"❤️ {poke[3] or 'Pokémon'} curado! HP: {new_hp}/{max_hp}")
        elif effect_type == "evolve":
            await ctx.send("Evolução por pedra em breve.")
        else:
            await ctx.send("Item não utilizável no momento.")
