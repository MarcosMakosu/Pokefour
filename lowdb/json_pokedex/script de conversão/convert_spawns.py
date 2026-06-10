import csv
import json
import re
from collections import defaultdict

CSV_FILE = "Cobblemon Spawns 1.6.1 - Sheet1.csv"
OUTPUT_JSON = "pokemon_spawns.json"


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

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


def parse_multipliers(value: str) -> dict:
    if not value:
        return {}

    value = value.replace(";", ",")

    multipliers = {}

    for part in value.split(","):
        part = part.strip()

        match = re.match(
            r"(.+?)\s*x\s*([0-9.]+)",
            part,
            re.IGNORECASE
        )

        if match:
            condition, factor = match.groups()

            multipliers[
                snake_case(condition)
            ] = float(factor)

    return multipliers


def parse_conditions(
    conditions_raw: str,
    anticonditions_raw: str
) -> dict:

    conditions = {}

    text = (
        f"{conditions_raw} {anticonditions_raw}"
    ).lower()

    moon_phases = [
        "new",
        "full",
        "first_quarter",
        "last_quarter",
        "waxing_crescent",
        "waxing_gibbous",
        "waning_crescent",
        "waning_gibbous"
    ]

    found_moons = []

    for moon in moon_phases:

        search = moon.replace("_", " ")

        if search in text:
            found_moons.append(moon)

    if found_moons:
        conditions["moon"] = found_moons

    structure_match = re.search(
        r"structure[:=]\s*([^,;]+)",
        text
    )

    if structure_match:
        conditions["structure"] = (
            structure_match.group(1).strip()
        )

    return conditions


def parse_light(
    sky_min,
    sky_max,
    can_see_sky
):
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

    special_columns = [
        "region_bias",
        "vivillon_wings",
        "flower",
        "sea",
        "striped",
        "bull_breed"
    ]

    for key in special_columns:

        value = row.get(key, "")

        if value:
            result[key] = split_field(value)

    return result


pokemon_data = {}
biome_index = defaultdict(
    lambda: defaultdict(set)
)

with open(
    CSV_FILE,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        raw_name = row.get(
            "Pokémon",
            ""
        ).strip()

        if not raw_name:
            continue

        pokemon_id = parse_pokemon_name(
            raw_name
        )

        bucket = (
            row.get("Bucket", "common")
            .strip()
            .lower()
        )

        try:
            weight = float(
                row.get("Weight", 1)
            )
        except:
            weight = 1.0

        try:
            min_level = int(
                row.get("Lv. Min", 1)
            )
        except:
            min_level = 1

        try:
            max_level = int(
                row.get(
                    "Lv. Max",
                    min_level
                )
            )
        except:
            max_level = min_level

        biomes = [
            snake_case(x)
            for x in split_field(
                row.get("Biomes", "")
            )
        ]

        excluded_biomes = [
            snake_case(x)
            for x in split_field(
                row.get(
                    "Excluded Biomes",
                    ""
                )
            )
        ]

        weather = [
            snake_case(x)
            for x in split_field(
                row.get("Weather", "")
            )
            if x.lower() != "any"
        ]

        time_conditions = [
            snake_case(x)
            for x in split_field(
                row.get("Time", "")
            )
            if x.lower() != "any"
        ]

        multipliers = parse_multipliers(
            row.get("Multipliers", "")
        )

        conditions = parse_conditions(
            row.get("Conditions", ""),
            row.get(
                "Anticonditions",
                ""
            )
        )

        light = parse_light(
            row.get("skyLightMin", ""),
            row.get("skyLightMax", ""),
            row.get("canSeeSky", "")
        )

        if light:
            conditions["light"] = light

        forms = extract_special_forms(row)

        spawn = {
            "bucket": bucket,
            "weight": weight,
            "levels": {
                "min": min_level,
                "max": max_level
            }
        }

        if biomes:
            spawn["biomes"] = biomes

        if excluded_biomes:
            spawn["excluded_biomes"] = (
                excluded_biomes
            )

        if weather:
            spawn["weather"] = weather

        if time_conditions:
            spawn["time"] = (
                time_conditions
            )

        if conditions:
            spawn["conditions"] = (
                conditions
            )

        if multipliers:
            spawn["multipliers"] = (
                multipliers
            )

        if forms:
            spawn["forms"] = forms

        if pokemon_id not in pokemon_data:

            pokemon_data[pokemon_id] = {
                "spawns": []
            }

        pokemon_data[pokemon_id][
            "spawns"
        ].append(spawn)

        for biome in biomes:
            biome_index[biome][
                bucket
            ].add(pokemon_id)


output = {
    "biomes": {
        biome: {
            rarity: sorted(
                list(pokemon_set)
            )
            for rarity, pokemon_set
            in rarity_data.items()
        }
        for biome, rarity_data
        in biome_index.items()
    },

    "pokemon": pokemon_data
}

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        output,
        file,
        ensure_ascii=False,
        indent=2
    )

print(
    f"✅ Gerado: {OUTPUT_JSON}"
)
print(
    f"📦 Pokémon: {len(pokemon_data)}"
)
print(
    f"🌎 Biomas: {len(biome_index)}"
)
