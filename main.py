import discord
import asyncio
from discord.ext import commands
from firebase import firebase
from elo_calculator import calculate_elo

client = commands.Bot(command_prefix='!')

with open('client_keys.txt') as keys:
    client_info = keys.readlines()

client_id = client_info[0].strip()
token = client_info[1].strip()

firebase_link = client_info[2].strip()
firebase = firebase.FirebaseApplication(firebase_link, None)

@client.command(
    name='elo',
    pass_context=True
)
async def get_elo(ctx):
    author = ctx.message.author
    elo_score = firebase.get('/members/' + author.id + '/elo_score', None)
    channel = ctx.message.channel
    await client.send_message(channel, str(author.name) + "'s elo is " + str(elo_score))

@client.command(
    name='board',
    pass_context=True
)
async def display_leaderboard(ctx):
    server = ctx.message.author.server
    channel = ctx.message.channel
    leaders = current_player = firebase.get('/members', None)
    leader_list = list(leaders.values())
    leader_list.sort(key=lambda k: k['elo_score'], reverse=True)
    smash_leader = []
    for leader in leader_list:
        if leader["has_smash_role"]:
            smash_leader.append(leader)

    await client.send_message(channel, 
    """
    The top Smash Players in {}:
    1. {} : {}
    2. {} : {}
    3. {} : {}
    4. {} : {}
    5. {} : {}
    """
    .format(server.name,
        smash_leader[0]['name'], smash_leader[0]['elo_score'],
        smash_leader[1]['name'], smash_leader[1]['elo_score'],
        smash_leader[2]['name'], smash_leader[2]['elo_score'],
        smash_leader[3]['name'], smash_leader[3]['elo_score'],
        smash_leader[4]['name'], smash_leader[4]['elo_score'],))

@client.command(
    name='match',
    pass_context=True
)
@commands.has_role(
    name='Match Mod'
)
async def declare_match(ctx, winner_tag, loser_tag):
    mentions = ctx.message.mentions
    channel = ctx.message.channel
    author = ctx.message.author
    winner_id = sanitize_mention(winner_tag)
    loser_id = sanitize_mention(loser_tag)
    winner = await client.get_user_info(winner_id)
    loser = await client.get_user_info(loser_id)
    winner_elo = firebase.get('/members/' + winner.id + '/elo_score', None)
    loser_elo = firebase.get('/members/' + loser.id + '/elo_score', None)
    winner_rating, loser_rating = calculate_elo(30, winner_elo, loser_elo)
    firebase.put('/', '/members/' + winner.id + '/',
    { 
        'name': winner.name,
        'elo_score': winner_rating
    })
    firebase.put('/', '/members/' + loser.id + '/',
    { 
        'name': loser.name,
        'elo_score': loser_rating
    })
    await client.send_message(channel, "{} : {}\n{} : {}".format(winner.name, winner_rating, loser.name, loser_rating))

@client.command(
    name='reset',
    pass_context=True
)
@commands.has_role(
    name='Match Mod'
)
async def reset_elo(ctx):
    members = ctx.message.author.server.members
    channel = ctx.message.channel
    role = discord.utils.find(lambda r: r.name == 'smash', ctx.message.author.server.roles)
    await client.send_message(channel, "RESETTING...");
    for member in members:
        has_smash_role = role in member.roles
        firebase.put('/', '/members/' + member.id + '/',
        { 
            'name': member.name,
            'elo_score': 1000,
            'has_smash_role': has_smash_role
        })
        print(member.id)
    await client.send_message(channel, "ELO RESET HAS BEEN COMPLETED")

@client.command(
    name='update',
    pass_context=True
)
@commands.has_role(
    name='Match Mod'
)
async def update(ctx):
    server = ctx.message.author.server
    channel = ctx.message.channel
    role = discord.utils.find(lambda r: r.name == 'smash', server.roles)
    await client.send_message(channel, "UPDATING...");
    await update_helper(server, role)
    await client.send_message(channel, "UPDATE HAS BEEN COMPLETED")

async def update_helper(server, role):
    for member in server.members:
        has_smash_role = role in member.roles
        elo_score = firebase.get('/members/' + member.id + '/elo_score', None)
        firebase.put('/', '/members/' + member.id + '/',
        { 
            'name': member.name,
            'elo_score': elo_score,
            'has_smash_role': has_smash_role
        })
        print(member.id)

@client.event
async def on_ready():
    print("Logged in as")
    print(str(client.user.name))
    print(str(client.user.id))
    print("-------------------")

@client.event
async def on_server_join(server):
    members = server.members
    role = discord.utils.find(lambda r: r.name == 'smash', server.roles)
    for member in members:
        has_smash_role = role in member.roles
        firebase.put('/', '/members/' + member.id + '/',
        { 
            'name': member.name,
            'elo_score': 1000,
            'has_smash_role': has_smash_role
        })
        print(member.id)

@client.event
async def on_member_join(member):
    firebase.put('/', '/members/' + member.id + '/',
    {
        'name': member.name,
        'elo_score': 1000,
        'has_smash_role': False
    })

@declare_match.error
async def match_declare_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.CheckFailure):
        await client.send_message(channel, "You don't have permission to declare matches.")

@reset_elo.error
async def reset_elo_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.CheckFailure):
        await client.send_message(channel, "You don't have permission to reset the ELO scores.")

@update.error
async def update_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.CheckFailure):
        await client.send_message(channel, "You don't have permission to update the database.")
            
async def dontcrash():
    channels = client.get_all_channels()
    asyncio.sleep(50)

def sanitize_mention(mention):
    user = mention.replace("<","")
    user = user.replace(">","")
    user = user.replace("!","")
    user = user.replace("@","")
    return user

client.loop.create_task(dontcrash())
client.run(token)
