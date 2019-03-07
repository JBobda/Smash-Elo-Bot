import discord
import asyncio

with open('client_keys.txt') as keys:
    client_info = keys.readlines()

client_id = client_info[0]
token = client_info[1].strip()

client = discord.Client()

@client.event
async def on_ready():
    print("Logged in as")
    print(str(client.user.name))
    print(str(client.user.id))
    print("-------------------")

@client.event
async def on_message(message):
    if message.content.startswith("!smash"):
        await client.send_message(message.channel, "This is a quick test!")

client.run(token)