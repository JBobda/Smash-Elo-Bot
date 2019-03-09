from discord.ext import commands
from firebase import firebase

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
        leader_list[0]['name'], leader_list[0]['elo_score'],
        leader_list[1]['name'], leader_list[1]['elo_score'],
        leader_list[2]['name'], leader_list[2]['elo_score'],
        leader_list[3]['name'], leader_list[3]['elo_score'],
        leader_list[4]['name'], leader_list[4]['elo_score'],))
        

    

@client.event
async def on_ready():
    print("Logged in as")
    print(str(client.user.name))
    print(str(client.user.id))
    print("-------------------")

@client.event
async def on_server_join(server):
    members = server.members
    for member in members:
        firebase.put('/', '/members/' + member.id + '/',
        { 
            'name': member.name,
            'elo_score': 1000
        })
        print(member.id)

@client.event
async def on_member_join(member):
    firebase.put('/', '/members/' + member.id + '/',
    {
        'name': member.name,
        'elo_score': 1000
    })
            
client.run(token)
