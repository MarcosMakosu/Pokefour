import random
from typing import Dict, List
from pokeapi import pokeapi

_base_stats_cache = {}

async def load_base_stats(species_id: int) -> Dict:
    if species_id in _base_stats_cache:
        return _base_stats_cache[species_id]
    data = await pokeapi.get_pokemon(species_id)
    if not data: return {}
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    types = [t["type"]["name"] for t in data["types"]]
    species_data = await pokeapi.get_species(species_id)
    catch_rate = species_data.get("capture_rate", 45)
    evo_chain_id = species_data.get("evolution_chain", {}).get("url", "").rstrip("/").split("/")[-1]
    result = {
        "name": data["name"],
        "types": types,
        "stats": stats,
        "catch_rate": catch_rate,
        "evolution_chain_id": evo_chain_id
    }
    _base_stats_cache[species_id] = result
    return result

def calc_hp(base_hp, iv, level, ev=0):
    return int((2 * base_hp + iv + ev // 4) * level // 100) + level + 10

def calc_other_stat(base_stat, iv, level, ev=0):
    return int(((2 * base_stat + iv + ev // 4) * level // 100) + 5)

def compute_capture_chance(catch_rate, ball_mult=1.0, biome_mod=1.0, time_mod=1.0):
    modified = catch_rate * ball_mult * biome_mod * time_mod
    modified = min(255, modified)
    return min(95, (modified / 255) * 100)

TYPE_CHART = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 2, "bug": 2, "rock": 0.5, "dragon": 0.5, "steel": 2},
    "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "electric": {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2, "ice": 0.5, "ground": 2, "flying": 2, "dragon": 2},
    "fighting": {"normal": 2, "ice": 2, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2, "ghost": 0, "steel": 2},
    "poison": {"grass": 2, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0},
    "ground": {"fire": 2, "electric": 2, "grass": 0.5, "poison": 2, "flying": 0, "bug": 0.5, "rock": 2, "steel": 2},
    "flying": {"grass": 2, "electric": 0.5, "fighting": 2, "bug": 2, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2, "poison": 2, "psychic": 0.5, "dark": 0, "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2, "ghost": 0.5, "dark": 2, "steel": 0.5},
    "rock": {"fire": 2, "ice": 2, "fighting": 0.5, "ground": 0.5, "flying": 2, "bug": 2, "steel": 0.5},
    "ghost": {"normal": 0, "psychic": 2, "ghost": 2, "dark": 0.5, "steel": 0.5},
    "dragon": {"dragon": 2, "steel": 0.5},
    "dark": {"fighting": 0.5, "psychic": 2, "ghost": 2, "dark": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2, "rock": 2, "steel": 0.5},
}

def get_type_effectiveness(move_type: str, defender_types: List[str]) -> float:
    mult = 1.0
    for t in defender_types:
        if move_type in TYPE_CHART and t in TYPE_CHART[move_type]:
            mult *= TYPE_CHART[move_type][t]
    return mult