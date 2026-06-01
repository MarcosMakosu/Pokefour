import discord, random, asyncio
from discord.ext import commands
from models import load_base_stats, calc_hp, compute_capture_chance
from pokeapi import pokeapi

BIOME_SPAWNS = {
    "floresta": [{"id": 1, "name": "Bulbasaur", "rarity": 5}, {"id": 16, "name": "Pidgey", "rarity": 40}],
    "agua":    [{"id": 129, "name": "Magikarp", "rarity": 50}, {"id": 118, "name": "Goldeen", "rarity": 30}],
    "caverna": [{"id": 74, "name": "Geodude", "rarity": 40}, {"id": 27, "name": "Sandshrew", "rarity": 30}]
}

class Spawns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spawn = {}
        self.last_spawn = {}

    async def get_biome(self, channel_id):
        async with self.bot.db.execute("SELECT biome FROM channel_biomes WHERE channel_id=?", (channel_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        ch_id = message.channel.id
        biome = await self.get_biome(ch_id)
        if not biome: return
        now = message.created_at.timestamp()
        if ch_id in self.last_spawn and now - self.last_spawn[ch_id] < 120: return
        if random.random() > 0.15: return
        pool = BIOME_SPAWNS.get(biome, [])
        if not pool: return
        species = random.choices(pool, weights=[p["rarity"] for p in pool], k=1)[0]
        level = random.randint(5, 15)
        shiny = random.randint(1, 4096) == 1
        self.active_spawn[ch_id] = {"species": species, "level": level, "shiny": shiny}
        self.last_spawn[ch_id] = now
        sprite = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{species['id']}.png"
        if shiny: sprite = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{species['id']}.png"
        embed = discord.Embed(title=f"Um {species['name']} selvagem apareceu!",
                              description="Digite `!catch` para tentar capturar.", color=0x2ecc71)
        embed.set_image(url=sprite)
        await message.channel.send(embed=embed)

    @commands.command()
    async def catch(self, ctx):
        spawn = self.active_spawn.pop(ctx.channel.id, None)
        if not spawn: return await ctx.send("Nenhum Pokémon selvagem no momento.")
        async with self.bot.db.execute(
            "SELECT i.item_name, i.quantity FROM inventory i JOIN shop_items s ON i.item_name=s.item_name "
            "WHERE i.user_id=? AND s.category='pokeballs' AND i.quantity>0 ORDER BY s.price DESC LIMIT 1", (ctx.author.id,)
        ) as cur:
            ball_row = await cur.fetchone()
        if not ball_row: return await ctx.send("Você não tem pokébolas!")
        ball_name, _ = ball_row
        species_data = await load_base_stats(spawn["species"]["id"])
        if not species_data: return await ctx.send("Erro ao carregar dados.")
        ball_mult = {"pokeball":1.0, "greatball":1.5, "ultraball":2.0, "netball":3.0}.get(ball_name, 1.0)
        hour = ctx.message.created_at.hour
        time_mod = 0.85 if hour < 6 or hour >= 18 else 1.0
        chance = compute_capture_chance(species_data["catch_rate"], ball_mult, 1.0, time_mod)
        if random.random() * 100 <= chance:
            ivs = {k: random.randint(0,31) for k in ["hp","atk","def","spa","spd","spe"]}
            max_hp = calc_hp(species_data["stats"]["hp"], ivs["hp"], spawn["level"])
            api_data = await pokeapi.get_pokemon(spawn["species"]["id"])
            lvl_moves = [m["move"]["url"].rstrip("/").split("/")[-1] for m in api_data.get("moves", [])
                         if m["version_group_details"][0]["level_learned_at"] <= 1]
            moves = lvl_moves[:2] if lvl_moves else [33, 45]
            await self.bot.db.execute(
                "INSERT INTO user_pokemon (user_id, species_id, level, iv_hp,iv_atk,iv_def,iv_spatk,iv_spdef,iv_speed, current_hp, moves, shiny) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (ctx.author.id, spawn["species"]["id"], spawn["level"],
                 ivs["hp"], ivs["atk"], ivs["def"], ivs["spa"], ivs["spd"], ivs["spe"],
                 max_hp, str(moves), int(spawn["shiny"])))
            await self.bot.db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE user_id=? AND item_name=?",
                                      (ctx.author.id, ball_name))
            await self.bot.db.commit()
            await ctx.send(f"{ctx.author.mention} capturou **{species_data['name']}** Lv.{spawn['level']} com uma {ball_name}!")
        else:
            await ctx.send("O Pokémon escapou!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setbiome(self, ctx, biome: str):
        await self.bot.db.execute("INSERT OR REPLACE INTO channel_biomes (channel_id, biome) VALUES (?,?)",
                                  (ctx.channel.id, biome.lower()))
        await self.bot.db.commit()
        await ctx.send(f"🌍 Bioma do canal definido para **{biome}**.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def forcespawn(self, ctx, species_id: int = None, level: int = None, *, flags: str = ""):
        """Força o spawn de um Pokémon (admin). Ex: !forcespawn 25 12 shiny"""
        biome = await self.get_biome(ctx.channel.id)
        if not biome:
            return await ctx.send("❌ Este canal não tem bioma. Use `!setbiome <biome>` primeiro.")

        # Se não especificou o ID, sorteia da tabela do bioma
        if species_id is None:
            pool = BIOME_SPAWNS.get(biome, [])
            if not pool:
                return await ctx.send("Bioma sem Pokémon cadastrados.")
            species = random.choices(pool, weights=[p["rarity"] for p in pool], k=1)[0]
            species_id = species["id"]
        
        # Define nível
        level = level or random.randint(5, 15)
        
        # Detecta shiny pela flag "shiny" ou "s" no texto
        shiny = "shiny" in flags.lower() or "s" in flags.lower()
        
        # Busca nome real (com tratamento de erro)
        try:
            data = await pokeapi.get_pokemon(species_id)
            name = data["name"].capitalize() if data else f"#{species_id}"
        except:
            name = f"#{species_id}"
        
        # Cria spawn ativo
        self.active_spawn[ctx.channel.id] = {
            "species": {"id": species_id, "name": name},
            "level": level,
            "shiny": shiny
        }
        self.last_spawn[ctx.channel.id] = ctx.message.created_at.timestamp()
        
        # Monta embed
        sprite = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{species_id}.png"
        if shiny: sprite = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/shiny/{species_id}.png"
        embed = discord.Embed(title=f"Um {name} selvagem apareceu! (Admin)",
                              description="Digite `!catch` para capturar.", color=0xff9900)
        embed.set_image(url=sprite)
        await ctx.send(embed=embed)