<p align="center">
  <img src="logo_prov.png" alt="Banner PokéFour" width="600"/>
</p>


# PokéFour - Bot Pokémon para Discord

![Versão](https://img.shields.io/badge/Versão-0.4.3--beta-orange)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.0+-7289DA?logo=discord&logoColor=white)
![Licença GPL v3](https://img.shields.io/badge/Licença-GPLv3-blue)
![GitHub release (latest)](https://img.shields.io/github/v/release/MarcosMakosu/pokefour)

![PokéAPI](https://img.shields.io/badge/PokéAPI-Dados%20Pokémon-EF5350?logo=pokemon&logoColor=white)
![OpenWeatherMap](https://img.shields.io/badge/OpenWeatherMap-Clima%20Real-1E90FF?logo=openweathermap&logoColor=white)

> ⚔️ Capture, evolua, batalhe e defenda estádios em um mundo Pokémon vivo, ligado ao clima e biomas reais!


| ⚠️ | **Atenção:** Este bot está em desenvolvimento beta. Comandos podem mudar!. |
| :--------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

---

## 🌍 Visão Geral

**PokéFour** é um bot do Discord que mergulha seu servidor no universo Pokémon clássico, com uma mecânicas de **biomas inspirados em cidades reais** e **spawns condicionados por clima, horário e fases da lua**.  
Enquanto os membros conversam, Pokémon selvagens surgem de acordo com o bioma e as condições climáticas da cidade vinculada ao canal. Capturas, batalhas, economia e um sistema de ranqueado trazem do bot uma experiência completa.

## ✨ Funcionalidades

- **Spawns inteligentes** – Pokémon aparecem automaticamente no chat, com base no bioma e condições reais (chuva, lua cheia, etc.).
- **Biomas reais** – Cada canal pode ser vinculado a uma cidade do mundo real. O Bioma e clima dessa cidade influencia os tipos de Pokémon que surgem.
- **Captura com pokébolas** – Use diferentes bolas (Net, Ultra, Dusk…) com multiplicadores que dependem do ambiente.
- **Batalhas por turnos** – Duelos PvP com movimentos, status e dano calculado como nos jogos oficiais.
- **Economia** – Colete moedas diárias, compre itens na loja (poções, TMs, pedras evolutivas) e gerencie seu inventário, ou venda para outros jogadores.
- **Estádios (Ginásios)** – Desafie o líder do estádio e defenda seu próprio ginásio por recompensas.
- **Ranqueado com apostas** – Suba do rank **Beginner** ao **Legend** disputando partidas valendo PokéCoins.
- **Administração poderosa** – Admins podem editar Pokémon de jogadores, gerenciar itens, forçar spawns e muito mais.

## 🌿 Sistema de Spawns Condicionais

Cada canal possui um **bioma** (definido via `!setbiome`) que está associado a uma **cidade real** no arquivo `biomes_config.json`. O bot verifica periodicamente o clima dessa cidade através da OpenWeatherMap e ajusta os spawns de acordo com as condições.

### Exemplo de `biomes_config.json`
```json
{
  "floresta": {
    "city": "Belém do Pará, BR",
    "lat": -1.455,
    "lon": -48.504
  },
  "deserto": {
    "city": "Dubai, AE",
    "lat": 25.2048,
    "lon": 55.2708
  }
}
```

### Condições de spawn (arquivo `spawn_conditions.json`)
Cada Pokémon pode ter condições especiais que aumentam sua taxa de aparição:
```json
{
  "129": {
    "name": "Magikarp",
    "boost": [
      {"condition": "weather.rain", "multiplier": 3.0},
      {"condition": "moon.full_moon", "multiplier": 1.5}
    ]
  }
}
```
- **weather.rain**: chuva reportada pela API de clima.
- **moon.full_moon**: lua cheia (obtida via OpenWeatherMap One Call).
- **time.night**: período noturno (baseado no fuso horário do servidor).

Assim, se chover em Belém do Pará, os canais com bioma **floresta** terão muito mais Magikarp, Goldeen e outros Pokémon aquáticos!



## 🧱 Tecnologias

- [discord.py 2.0+](https://github.com/Rapptz/discord.py)
- [PokéAPI](https://pokeapi.co/) – dados oficiais de Pokémon, movimentos, evoluções e sprites.
- [OpenWeatherMap One Call API 3.0](https://openweathermap.org/api/one-call-3) – clima e fases da lua gratuitos (plano free).
- [aiohttp](https://docs.aiohttp.org/) – requisições assíncronas.
- [aiosqlite](https://github.com/omnilib/aiosqlite) – banco de dados leve e assíncrono.


## 🔧🕹️ Comandos Principais

| Comando | Descrição |
|---------|-----------|
| `!daily` | Coleta de moedas diárias (bônus por streak) |
| `!balance` / `!money` | Exibe seu saldo em PokéDólares |
| `!shop` | Abre a PokéShop com itens à venda |
| `!buy <item> [qtd]` | Compra itens (ex: `!buy pokeball 5`) |
| `!bag` | Mostra sua mochila |
| `!use <item> <id/nome>` | Usa um item (poção, pedra, etc.) |
| `!catch` | Tenta capturar o Pokémon selvagem ativo no canal |
| `!setbiome <bioma>` | (Admin) Define o bioma do canal atual |
| `!forcespawn [id] [nível] [shiny]` | (Admin) Força o spawn de um Pokémon específico |
| `!editpokemon @user <id> <campo> <valor>` | (Admin) Edita um Pokémon de qualquer jogador |
| `!duel @oponente` | Inicia uma batalha PvP (em desenvolvimento) |
| `!rduel @oponente <aposta>` | Desafia alguém no ranqueado com aposta |
| `!queue <aposta>` | Entra na fila de matchmaking ranqueado |
| `!profile [@user]` | Mostra perfil ranqueado |
| `!lb` | Exibe o top 10 do servidor |
| `!stadium` | Desafia o estádio do canal atual |

> 📌 **Nota:** Para usar os comandos de batalha, o bot criará canais privados temporários. Assegure-se de que ele tenha permissão de `Manage Channels`.


## 🌤️ APIs Externas Utilizadas

- **Clima e Lua**: [OpenWeatherMap One Call API 3.0](https://openweathermap.org/api/one-call-3)  

- **Hora local**: O bot usa o fuso horário configurado no servidor Discord para determinar dia/noite.

## 🚧 Funcionalidades em Desenvolvimento

- [ ] **Batalhas completas** com troca de Pokémon, itens e habilidades.
- [ ] **Sistema de estádios** totalmente funcional (time do bot, troca de líder).
- [ ] **Lojas rotativas e eventos especiais** (Torneios de Captura, Double Score Weekend).
- [ ] **Integração com fuso horário local** para precisão do ciclo dia/noite.
- [ ] **Mais cidades e biomas** na configuração padrão.

## 🚧 Gerações adicionadas

- Geração 1 | 001 - 151 


---

<details>
<summary> 📋 Guia de Instalação</summary>

## ⚙️ Instalação

1. **Clone o repositório**  
   ```bash
   git clone https://github.com/seu-usuario/pokefour.git
   cd pokefour
   ```

2. **Crie e ative um ambiente virtual**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   ```

3. **Instale as dependências**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o bot**  
   Crie um arquivo `config.py` baseado no exemplo abaixo e preencha com seu token, ID do cargo de admin e chave da OpenWeatherMap:
   ```python
   TOKEN = "seu_token_aqui"
   ADMIN_ROLE_ID = 1234567890
   WEATHER_API_KEY = "sua_chave_openweather"
   ```

5. **Execute o bot**  
   ```bash
   python main.py
   ```
</details>

---
## 🤝 Pendencias e Como Contribuir

### Banco de Dados
 Temos dois arquivos em JSON, um para os pokemons e suas **Condições Multiplicadoras** e o de **Movimentos Especiais**. 
- O banco de dados de **condições multiplicadoras** carece de informações que poderiam trazer mais dinamica ao sistema de spawn do pokemon, informações que poderiam ser preenchidas com base em ardua leitura da pokedex.  
- O banco de dados dos **Movimentos especiais** carecem de serem programadas seguindo o alinhamento do [JSON](lowdb/special_moves.json), vale fazer leitura do [Codigo do Sistema de batalha](cogs/battles.py)

### codigo
1. Fork o projeto.
2. Crie uma branch: `git checkout -b minha-feature`.
3. Faça suas alterações e commit: `git commit -m 'Minha nova feature'`.
4. Push: `git push origin minha-feature`.
5. Abra um Pull Request.

Sugestões, relatórios de bugs e ideias são muito bem-vindos! Use as [issues](https://github.com/seu-usuario/pokefour/issues).

## 📜 Licença

Distribuído sob a licença GPL 3.0. Veja `LICENSE` para mais informações.

---

*Feito com ☕ por Marquinhos*  
*Pokémon é uma marca registrada da Nintendo, Game Freak e Creatures Inc.*
*Por favor Nitendo não me processe*

```
