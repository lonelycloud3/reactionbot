import os
import datetime
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))
ROLES_TO_MENTION = os.getenv('ROLES_TO_MENTION')
import discord

intents = discord.Intents.default()
intents.reactions = True

client = discord.Client(intents=intents)

reactions = {}

def does_time_differ_30_min(timestamp1: datetime.datetime, timestamp2: datetime.datetime):
    delta = timestamp2 - timestamp1
    mins = delta.total_seconds() / 60
    print(mins)
    return mins >= 30
        
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_raw_reaction_add(payload):
    if CHANNEL_ID is not None and payload.channel_id == CHANNEL_ID:
        now = datetime.datetime.now()
        if payload.user_id not in reactions:
            reactions[payload.user_id] = [(payload.message_id, payload.emoji, now)]
        else:
            reactions[payload.user_id].append((payload.message_id, payload.emoji, now))
        reactions[payload.user_id] = list(filter(lambda x: not does_time_differ_30_min(x[2], now), reactions[payload.user_id]))
        if len(reactions[payload.user_id]) > 3:
            roles = ROLES_TO_MENTION.split(',')
            roles = list(map(lambda x: f'<@&{x}>', roles))
            mentions = ' '.join(roles)
            message = f"{mentions} {payload.member.name} сделал больше чем 3 реакции за 30 минут!"
            channel = client.get_channel(CHANNEL_ID)
            reactions[payload.user_id].clear()
            await channel.send(message)

@client.event
async def on_raw_reaction_remove(payload):
    if CHANNEL_ID is not None and payload.channel_id == CHANNEL_ID:
        if payload.user_id in reactions:
            reactions[payload.user_id] = list(filter(lambda x: x[0] != payload.message_id and x[1] != payload.emoji, reactions[payload.user_id]))



client.run(TOKEN)
