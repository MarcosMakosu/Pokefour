import aiosqlite

async def init_db(db):
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS player_economy (
            user_id BIGINT PRIMARY KEY,
            pokedollars INT DEFAULT 0,
            last_daily TIMESTAMP,
            streak INT DEFAULT 0,
            total_claimed INT DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS player_ranks (
            user_id BIGINT PRIMARY KEY,
            score INT DEFAULT 0,
            wins INT DEFAULT 0,
            losses INT DEFAULT 0,
            win_streak INT DEFAULT 0,
            best_streak INT DEFAULT 0,
            total_battles INT DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS inventory (
            user_id BIGINT,
            item_name TEXT,
            quantity INT DEFAULT 1,
            PRIMARY KEY (user_id, item_name)
        );
        CREATE TABLE IF NOT EXISTS user_pokemon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id BIGINT,
            species_id INT,
            nickname TEXT,
            level INT,
            xp INT DEFAULT 0,
            iv_hp INT, iv_atk INT, iv_def INT,
            iv_spatk INT, iv_spdef INT, iv_speed INT,
            current_hp INT,
            moves TEXT,
            shiny INT DEFAULT 0,
            is_defending INT DEFAULT 0,
            caught_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS channel_biomes (
            channel_id BIGINT PRIMARY KEY,
            biome TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS stadiums (
            channel_id BIGINT PRIMARY KEY,
            owner_id BIGINT,
            defender1_id INTEGER,
            defender2_id INTEGER,
            defender3_id INTEGER,
            biome TEXT,
            claimed_at TIMESTAMP,
            last_reward TIMESTAMP,
            FOREIGN KEY (defender1_id) REFERENCES user_pokemon(id),
            FOREIGN KEY (defender2_id) REFERENCES user_pokemon(id),
            FOREIGN KEY (defender3_id) REFERENCES user_pokemon(id)
        );
        CREATE TABLE IF NOT EXISTS shop_items (
            item_name TEXT PRIMARY KEY,
            category TEXT,
            price INT,
            description TEXT,
            effect_type TEXT,
            effect_value TEXT,
            emoji TEXT,
            stock INT DEFAULT -1
        );
    """)
    await db.commit()