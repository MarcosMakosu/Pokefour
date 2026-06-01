import aiohttp
from typing import Dict, Optional

class PokeAPI:
    BASE = "https://pokeapi.co/api/v2"
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = {}

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def fetch(self, endpoint: str) -> Dict:
        if endpoint in self.cache:
            return self.cache[endpoint]
        session = await self._get_session()
        url = f"{self.BASE}/{endpoint}"
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                self.cache[endpoint] = data
                return data
        return {}

    async def get_pokemon(self, identifier):
        return await self.fetch(f"pokemon/{identifier}")

    async def get_species(self, identifier):
        return await self.fetch(f"pokemon-species/{identifier}")

    async def get_move(self, id):
        return await self.fetch(f"move/{id}")

    async def get_evolution_chain(self, id):
        return await self.fetch(f"evolution-chain/{id}")

    async def get_type(self, name):
        return await self.fetch(f"type/{name}")

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Instância global
pokeapi = PokeAPI()