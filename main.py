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
