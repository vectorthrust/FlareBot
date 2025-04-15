import discord
import os
import requests
from typing import NoReturn
from qdrant_client import QdrantClient
from FlareBot.ai import GeminiEmbedding
from FlareBot.retriever.qdrant_collection import store_discord_message
from FlareBot.retriever.config import RetrieverConfig
from FlareBot.settings import settings
from FlareBot.utils import load_json
from FlareBot.state import app_state

TOKEN = settings.discord_bot_token

# List of authorized user IDs whose messages should be stored
AUTHORIZED_USER_IDS = [
    "809188856242503720", 
]

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Enable message content intent

client = discord.Client(intents=intents)

def initialize_clients() -> None:
    """Initialize the required clients and store them in app_state"""
    if not all([app_state.qdrant_client, app_state.retriever_config, app_state.embedding_client]):

        config_json = load_json(settings.input_path / "input_parameters.json")
        retriever_config = RetrieverConfig.load(config_json["retriever_config"])
        
        app_state.qdrant_client = QdrantClient(host=retriever_config.host, port=retriever_config.port)
        app_state.retriever_config = retriever_config
        app_state.embedding_client = GeminiEmbedding(api_key=settings.gemini_api_key)

@client.event
async def on_ready() -> None:
    print(f'Logged in as {client.user}')
    initialize_clients()

@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    
    stored_successfully = False

    if message.content.startswith("!norag"):

        norag_content = message.content[len("!norag"):].strip()
        
        if norag_content:
            url = "http://localhost/api/routes/chat/"
            data = {"message": message.content}

            response = requests.post(url, json=data)

            if response.status_code == 200:
                await message.reply(response.json()["response"])
            else:
                print(f"Error: {response.status_code}, {response.text}")
        else:
            await message.reply("Please provide content after `!norag`.")
        return

    if str(message.author.id) in AUTHORIZED_USER_IDS:
        try:
            initialize_clients()
            
            if (app_state.qdrant_client is not None and 
                app_state.retriever_config is not None and 
                app_state.embedding_client is not None):
                
                await store_discord_message(
                    jump_url=message.jump_url,
                    message_content=message.content,
                    author_id=str(message.author.id),
                    qdrant_client=app_state.qdrant_client,
                    retriever_config=app_state.retriever_config,
                    embedding_client=app_state.embedding_client,
                )
                stored_successfully = True
            else:
                print("Failed to store message: clients not properly initialized")
        except Exception as e:
            print(f"Failed to store message in vector database: {str(e)}")

    if stored_successfully:
        return
    
    url = "http://localhost/api/routes/chat/"
    data = {"message": message.content}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        await message.reply(response.json()["response"])
    else:
        print(f"Error: {response.status_code}, {response.text}")

        
async def start_bot() -> NoReturn:
    await client.start(TOKEN)

