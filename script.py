import csv
import json
import re
from collections import defaultdict


CSV_FILE = "pokemon.csv"
OUTPUT_FILE = "pokemon_spawns.json"


def snake_case(text):
    text = text.strip().lower()

    text = re.sub(r"[()]", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)

    return text.strip("_")


def split_field(value):
    if not value:
        return []

    separators = [";", ","]

    result = [value]

    for sep in separators:
        temp = []

        for item in result:
            temp.extend(item.split(sep))

        result = temp

    return [
        item.strip()
        for item in result
        if item.strip()
    ]


data = {
    "biomes": {},
    "pokemon": {}
}


biomes = defaultdict(
    lambda: {
        "common": [],
        "uncommon": [],
        "rare": [],
        "ultra_rare": []
    }
)


with open(CSV_FILE, encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        name = row.get("Pokemon", "").strip()

        if not name:
            continue

        pokemon_id = snake_case(name)

        bucket = snake_case(
            row.get("Bucket", "common")
        )

        weight = int(
            row.get("Weight", 1) or 1
        )

        min_level = int(
            row.get("Min Level", 1) or 1
        )

        max_level = int(
            row.get("Max Level", min_level) or min_level
        )

        biome_list = split_field(
            row.get("Biomes", "")
        )

        excluded_biomes = split_field(
            row.get("Excluded Biomes", "")
        )

        weather = [
            snake_case(x)
            for x in split_field(
                row.get("Weather", "")
            )
        ]

        time_conditions = [
            snake_case(x)
            for x in split_field(
                row.get("Time", "")
            )
        ]

        moon_conditions = [
            snake_case(x)
            for x in split_field(
                row.get("Moon", "")
            )
        ]

        pokemon = {
            "bucket": bucket,
            "weight": weight,
            "levels": {
                "min": min_level,
                "max": max_level
            },
            "biomes": biome_list
        }

        if excluded_biomes:
            pokemon["excluded_biomes"] = excluded_biomes

        conditions = {}

        if weather:
            conditions["weather"] = weather

        if time_conditions:
            conditions["time"] = time_conditions

        if moon_conditions:
            conditions["moon"] = moon_conditions

        if conditions:
            pokemon["conditions"] = conditions

        forms = []

        for key in (
            "region_bias",
            "vivillon_wings",
            "flower",
            "sea",
            "striped",
            "bull_breed"
        ):

            value = row.get(key, "").strip()

            if value:
                forms.extend(
                    split_field(value)
                )

        if forms:
            pokemon["forms"] = forms

        data["pokemon"][pokemon_id] = pokemon

        for biome in biome_list:

            if bucket not in biomes[biome]:
                biomes[biome][bucket] = []

            biomes[biome][bucket].append(
                pokemon_id
            )


data["biomes"] = dict(biomes)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        data,
        file,
        ensure_ascii=False,
        separators=(",", ":")
    )


print(
    f"Arquivo gerado: {OUTPUT_FILE}"
)
