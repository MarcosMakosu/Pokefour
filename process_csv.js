const fs = require('fs');
const path = '/home/marquinhos/Documentos/projetos/Pokefour/Cobblemon Spawns 1.6.1 - Sheet1.csv';

// Read the CSV file
const csv = fs.readFileSync(path, 'utf8');

// Split into lines
const lines = csv.split('\n').filter(l => l.trim() !== '');
console.error(`Processing ${lines.length} total lines (${lines.length - 1} data rows)`);

// Helper to parse a CSV line into fields (handles quoted commas)
function parseCSVLine(line) {
  const fields = [];
  let current = '';
  let inQuotes = false;
  for (let ch of line) {
    if (ch === '"') {
      inQuotes = !inQuotes;
    } else if (ch === ',' && !inQuotes) {
      fields.push(current);
      current = '';
    } else {
      current += ch;
    }
  }
  fields.push(current);
  // Now trim and remove surrounding quotes
  return fields.map(f => {
    let v = f.trim();
    if (v.startsWith('"') && v.endsWith('"')) {
      v = v.substring(1, v.length - 1).replace(/""/g, '"');
    }
    return v;
  });
}

// We'll accumulate data per pokemon (lowercase name)
const pokemonMap = new Map();

// Process each line (skip header)
for (let i = 1; i < lines.length; i++) {
  const line = lines[i];
  if (line.trim() === '') continue;
  const fields = parseCSVLine(line);
  // We expect at least 19 fields (0 to 18). If not, skip.
  if (fields.length < 19) continue;

  const [, pokemon, entry, bucket, weightStr, lvMinStr, lvMaxStr, biomesStr, excludedBiomesStr, timeStr, weatherStr, multipliersStr, contextStr, presetsStr, conditionsStr, anticonditionsStr, skyLightMinStr, skyLightMaxStr, canSeeSkyStr] = fields;

  const name = pokemon.toLowerCase();
  if (!name) continue;

  // Get or create accumulator for this pokemon
  let acc = pokemonMap.get(name);
  if (!acc) {
    acc = {
      bucket: '',
      weight: 0,
      minLevel: NaN,
      maxLevel: NaN,
      biomes: new Set(),
      excludedBiomes: new Set(),
      weather: new Set(),
      time: new Set()
    };
    pokemonMap.set(name, acc);
  }

  // Update bucket if not set
  if (!acc.bucket && bucket) {
    acc.bucket = bucket;
  }
  // Update weight
  const weight = parseFloat(weightStr);
  if (!isNaN(weight) && (acc.weight === 0 || isNaN(acc.weight))) {
    acc.weight = weight;
  }
  // Update levels
  const minLevel = parseInt(lvMinStr, 10);
  const maxLevel = parseInt(lvMaxStr, 10);
  if (!isNaN(minLevel) && isNaN(acc.minLevel)) {
    acc.minLevel = minLevel;
  }
  if (!isNaN(maxLevel) && isNaN(acc.maxLevel)) {
    acc.maxLevel = maxLevel;
  }

  // Parse biomes
  if (biomesStr) {
    const biomes = biomesStr.split(',').map(b => b.trim()).filter(b => b);
    for (const b of biomes) {
      acc.biomes.add(b);
    }
  }
  // Parse excluded biomes
  if (excludedBiomesStr) {
    const excluded = excludedBiomesStr.split(',').map(b => b.trim()).filter(b => b);
    for (const b of excluded) {
      acc.excludedBiomes.add(b);
    }
  }

  // Parse time (if not "any")
  if (timeStr && timeStr.toLowerCase() !== 'any') {
    const times = timeStr.split(',').map(t => t.trim()).filter(t => t);
    for (const t of times) {
      acc.time.add(t);
    }
  }
  // Parse weather (if not "any")
  if (weatherStr && weatherStr.toLowerCase() !== 'any') {
    const weathers = weatherStr.split(',').map(w => w.trim()).filter(w => w);
    for (const w of weathers) {
      acc.weather.add(w);
    }
  }
}

// Now build final objects
const biome_index = {};
const pokemon_data = {};

for (const [name, acc] of pokemonMap.entries()) {
  // Ensure we have default values for levels if still NaN
  const minLevel = isNaN(acc.minLevel) ? 0 : acc.minLevel;
  const maxLevel = isNaN(acc.maxLevel) ? 100 : acc.maxLevel;

  // Build pokemon_data entry according to specification
  pokemon_data[name] = {
    bucket: acc.bucket,
    weight: acc.weight,
    levels: {
      min: minLevel,
      max: maxLevel
    },
    biomes: Array.from(acc.biomes).sort(),
    excluded_biomes: Array.from(acc.excludedBiomes).sort(),
    off_biome_spawn: {
      enabled: false, // Default as no data in CSV
      multiplier: 0   // Default as no data in CSV
    },
    conditions: {
      weather: Array.from(acc.weather).sort(),
      time: Array.from(acc.time).sort(),
      moon: [] // No moon data in CSV
    },
    multipliers: {}, // No multiplier data in CSV (left as empty object)
    forms: [] // No form data in CSV (left as empty array)
  };

  // Build biome_index
  for (const biome of acc.biomes) {
    if (!biome_index[biome]) {
      biome_index[biome] = [];
    }
    if (!biome_index[biome].includes(name)) {
      biome_index[biome].push(name);
    }
  }
}

// Sort biome_index arrays for consistency
for (const biome in biome_index) {
  biome_index[biome].sort();
}

// Output the two JSON objects on separate lines
// First, biome_index
console.log(JSON.stringify(biome_index));
// Second, pokemon_data
console.log(JSON.stringify(pokemon_data));