import asyncio
import aiosqlite
import discord
from discord.ext import commands
from config import TOKEN, DB_PATH
from database import init_db
from pokeapi import pokeapi

async def main():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    bot.db = await aiosqlite.connect(DB_PATH)
    await init_db(bot.db)   # <-- aqui a correção

    @bot.event
    async def on_ready():
        print(f"{bot.user} conectado!")
        async with bot.db.execute("SELECT COUNT(*) FROM shop_items") as cur:
            if (await cur.fetchone())[0] == 0:
                items = [
                    ("pokeball", "pokeballs", 200, "Bola padrão (1x)", "capture", '{"ball_multiplier":1.0}', "🔴"),
                    ("greatball", "pokeballs", 600, "Boa (1.5x)", "capture", '{"ball_multiplier":1.5}', "🔵"),
                    ("ultraball", "pokeballs", 1200, "Ultra (2x)", "capture", '{"ball_multiplier":2.0}', "🟡"),
                    ("potion", "healing", 300, "Cura 20 HP", "heal", '{"hp_restore":20}', "🧪"),
                    ("superpotion", "healing", 700, "Cura 50 HP", "heal", '{"hp_restore":50}', "🧪"),
                    ("firestone", "evolution", 3000, "Evolui Pokémon de Fogo", "evolve", '{"stone":"fire"}', "🔥"),
                    ("waterstone", "evolution", 3000, "Evolui Pokémon de Água", "evolve", '{"stone":"water"}', "💧"),
                    ("thunderstone", "evolution", 3000, "Evolui Pokémon Elétricos", "evolve", '{"stone":"thunder"}', "⚡"),
                ]
                await bot.db.executemany(
                    "INSERT OR IGNORE INTO shop_items (item_name, category, price, description, effect_type, effect_value, emoji) VALUES (?,?,?,?,?,?,?)",
                    items)
                await bot.db.commit()

    # Carregar cogs
    from cogs.spawns import Spawns
    from cogs.economy import Economy
    from cogs.admin import Admin
    from cogs.battles import Battles
    from cogs.ranked import Ranked
    from cogs.stadium import Stadium
    from cogs.events import Events

    await bot.add_cog(Spawns(bot))
    await bot.add_cog(Economy(bot))
    await bot.add_cog(Admin(bot))
    await bot.add_cog(Battles(bot))
    await bot.add_cog(Ranked(bot))
    await bot.add_cog(Stadium(bot))
    await bot.add_cog(Events(bot))

    try:
        await bot.start(TOKEN)
    finally:
        await pokeapi.close()
        await bot.db.close()

asyncio.run(main())