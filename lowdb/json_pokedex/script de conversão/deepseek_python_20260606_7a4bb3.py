import csv
import json
import re
from collections import defaultdict

CSV_FILE = "Cobblemon Spawns 1.6.1 - Sheet1.csv"
OUTPUT_JSON = "pokemon_spawns.json"

# Mapeamento de biomas originais (como aparecem no CSV) para nomes temáticos de Pokémon
BIOME_MAP = {
    "Aether": "Céu de Ho-Oh",
    "Arid": "Deserto de Orre",
    "Badlands": "Cânion de Rota 111",
    "Bamboo": "Floresta de Bambu",
    "Beach": "Praia de Humilau",
    "Bumblezone": "Colmeia de Vespiquen",
    "Cherry Blossom": "Bosque das Cerejeiras",
    "Coast": "Litoral de Hoenn",
    "Cold": "Tundra Glacial",
    "Cold Ocean": "Mar Glacial",
    "Crystal Canyon": "Caverna Cristal",
    "Crystalline Chasm": "Abismo Cristalino",
    "Deep Dark": "Caverna Abissal",
    "Deep Ocean": "Fossa Oceânica",
    "Desert": "Grande Deserto de Orre",
    "Dripstone": "Caverna Estalactite",
    "End": "Espaço Ultra",
    "Floral": "Prado Florido",
    "Floral Meadow": "Campina das Flabebe",
    "Forest": "Bosque Verde",
    "Freezing": "Pico Gelado",
    "Freshwater": "Lago da Serenidade",
    "Frozen Ocean": "Mar Congelado",
    "Frozen River": "Rio Glacial",
    "Glacial": "Calota Polar",
    "Grassland": "Pradaria",
    "Highlands": "Planalto Áspero",
    "Hills": "Colinas Verdejantes",
    "Howling Constructs": "Ruínas Uivantes",
    "Island": "Arquipélago",
    "Jungle": "Selva Tropical",
    "Lukewarm Ocean": "Mar Temperado",
    "Lush": "Selva Úmida",
    "Magical": "Bosque Encantado",
    "Mountain": "Cordilheira",
    "Muddy": "Pântano Lamacento",
    "Mushroom": "Bosque dos Cogumelos",
    "Mushroom Fields": "Campos Cogumelo",
    "Nether": "Terras Vulcânicas",
    "Nether Basalt": "Colunas de Basalto",
    "Nether Crimson": "Bosque Carmesim",
    "Nether Desert": "Deserto de Cinzas",
    "Nether Forest": "Floresta Ígnea",
    "Nether Frozen": "Gelo Infernal",
    "Nether Fungus": "Floresta de Fungos",
    "Nether Mountain": "Pico Vulcânico",
    "Nether Overgrowth": "Vegetação Abrasadora",
    "Nether Quartz": "Mina de Cristais",
    "Nether Soul Fire": "Chama Espiritual",
    "Nether Soul Sand": "Areia das Almas",
    "Nether Toxic": "Pântano Tóxico",
    "Nether Warped": "Distorção Carmesim",
    "Nether Wasteland": "Planície Devastada",
    "Ocean": "Mar Aberto",
    "Overworld": "Mundo Pokémon",
    "Peak": "Cume dos Céus",
    "Plains": "Planície Serena",
    "Plateau": "Planalto Antigo",
    "Pollinated Fields": "Campo Polinizado",
    "River": "Rio Sereno",
    "Sandy": "Dunas de Areia",
    "Savanna": "Savana",
    "Sky": "Céu Infinito",
    "Skyroot Forest": "Floresta Etérea",
    "Skyroot Grove": "Bosque Celeste",
    "Skyroot Meadow": "Prado Flutuante",
    "Skyroot Woodland": "Bosque Aéreo",
    "Snowy Beach": "Praia Nevada",
    "Snowy Forest": "Floresta Branca",
    "Snowy Taiga": "Taiga Glacial",
    "Spooky": "Cemitério Sombrio",
    "Sunflower Plains": "Campo de Girassóis",
    "Swamp": "Grande Pântano",
    "Taiga": "Taiga Fria",
    "Temperate": "Zona Temperada",
    "Thermal": "Bacia Termal",
    "Tropical Island": "Paraíso Tropical",
    "Tundra": "Tundra Ártica",
    "Volcanic": "Região Vulcânica",
    "Warm Ocean": "Mar Quente"
}


def snake_case(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[\[\]\(\)]", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def parse_pokemon_name(name: str) -> str:
    match = re.match(r"(.+?)\s*\[(.+?)\]", name.strip())
    if match:
        base, form = match.groups()
        return f"{snake_case(base)}_{snake_case(form)}"
    return snake_case(name)


def split_field(value: str) -> list:
    if not value:
        return []
    value = value.replace(";", ",")
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_multipliers(value: str) -> dict:
    if not value:
        return {}
    value = value.replace(";", ",")
    multipliers = {}
    for part in value.split(","):
        part = part.strip()
        match = re.match(r"(.+?)\s*x\s*([0-9.]+)", part, re.IGNORECASE)
        if match:
            condition, factor = match.groups()
            multipliers[snake_case(condition)] = float(factor)
    return multipliers


def parse_conditions(conditions_raw: str, anticonditions_raw: str) -> dict:
    conditions = {}
    text = f"{conditions_raw} {anticonditions_raw}".lower()
    moon_phases = [
        "new", "full", "first_quarter", "last_quarter",
        "waxing_crescent", "waxing_gibbous",
        "waning_crescent", "waning_gibbous"
    ]
    found_moons = []
    for moon in moon_phases:
        search = moon.replace("_", " ")
        if search in text:
            found_moons.append(moon)
    if found_moons:
        conditions["moon"] = found_moons
    structure_match = re.search(r"structure[:=]\s*([^,;]+)", text)
    if structure_match:
        conditions["structure"] = structure_match.group(1).strip()
    return conditions


def parse_light(sky_min, sky_max, can_see_sky):
    light = {}
    if sky_min:
        light["min"] = int(sky_min)
    if sky_max:
        light["max"] = int(sky_max)
    if str(can_see_sky).lower() == "true":
        light["can_see_sky"] = True
    elif str(can_see_sky).lower() == "false":
        light["can_see_sky"] = False
    return light


def extract_special_forms(row):
    result = {}
    special_columns = ["region_bias", "vivillon_wings", "flower", "sea", "striped", "bull_breed"]
    for key in special_columns:
        value = row.get(key, "")
        if value:
            result[key] = split_field(value)
    return result


def map_biomes(biome_list):
    """Aplica o mapeamento de biomas, mantendo o nome original se não houver tradução."""
    mapped = []
    for biome in biome_list:
        # Remove espaços extras e tenta encontrar no mapa
        original = biome.strip()
        mapped_name = BIOME_MAP.get(original, original)
        mapped.append(mapped_name)
    return mapped


pokemon_data = {}
biome_index = defaultdict(lambda: defaultdict(set))

with open(CSV_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        raw_name = row.get("Pokémon", "").strip()
        if not raw_name:
            continue

        pokemon_id = parse_pokemon_name(raw_name)
        bucket = row.get("Bucket", "common").strip().lower()
        try:
            weight = float(row.get("Weight", 1))
        except:
            weight = 1.0
        try:
            min_level = int(row.get("Lv. Min", 1))
        except:
            min_level = 1
        try:
            max_level = int(row.get("Lv. Max", min_level))
        except:
            max_level = min_level

        # Biomas: converte a lista original e depois aplica o mapeamento (sem snake_case)
        original_biomes = split_field(row.get("Biomes", ""))
        biomes = map_biomes(original_biomes)

        # Biomas excluídos: também mapeados
        original_excluded = split_field(row.get("Excluded Biomes", ""))
        excluded_biomes = map_biomes(original_excluded)

        weather = [snake_case(x) for x in split_field(row.get("Weather", "")) if x.lower() != "any"]
        time_conditions = [snake_case(x) for x in split_field(row.get("Time", "")) if x.lower() != "any"]
        multipliers = parse_multipliers(row.get("Multipliers", ""))
        conditions = parse_conditions(row.get("Conditions", ""), row.get("Anticonditions", ""))
        light = parse_light(row.get("skyLightMin", ""), row.get("skyLightMax", ""), row.get("canSeeSky", ""))
        if light:
            conditions["light"] = light
        forms = extract_special_forms(row)

        spawn = {
            "bucket": bucket,
            "weight": weight,
            "levels": {"min": min_level, "max": max_level}
        }

        if biomes:
            spawn["biomes"] = biomes
        if excluded_biomes:
            spawn["excluded_biomes"] = excluded_biomes
        if weather:
            spawn["weather"] = weather
        if time_conditions:
            spawn["time"] = time_conditions
        if conditions:
            spawn["conditions"] = conditions
        if multipliers:
            spawn["multipliers"] = multipliers
        if forms:
            spawn["forms"] = forms

        if pokemon_id not in pokemon_data:
            pokemon_data[pokemon_id] = {"spawns": []}
        pokemon_data[pokemon_id]["spawns"].append(spawn)

        # Índice de biomas (agora com os nomes mapeados)
        for biome in biomes:
            biome_index[biome][bucket].add(pokemon_id)

# Estrutura final
output = {
    "biomes": {
        biome: {
            rarity: sorted(list(pokemon_set))
            for rarity, pokemon_set in rarity_data.items()
        }
        for biome, rarity_data in biome_index.items()
    },
    "pokemon": pokemon_data
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
    json.dump(output, file, ensure_ascii=False, indent=2)

print(f"✅ Gerado: {OUTPUT_JSON}")
print(f"📦 Pokémon: {len(pokemon_data)}")
print(f"🌎 Biomas: {len(biome_index)}")