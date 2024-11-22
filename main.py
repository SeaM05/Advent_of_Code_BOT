import os
import time
import datetime
import json
import urllib.request
from dotenv import load_dotenv

from discord.ext import commands
import discord

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
URL = os.getenv('AOC_URL')
COOKIE = os.getenv('AOC_COOKIE')
LEADERBOARD = os.getenv('AOC_LEADERBOARD_CODE')
POLL_MINS = 15  # Advent Of Code request that you don't poll their API more often than once every 15 minutes

MAX_MESSAGE_LEN = 2000 - 6
PLAYER_STR_FORMAT = '{rank:2}) {name:{name_pad}} ({points:{points_pad}}) {stars:{stars_pad}}* ({star_time})\n'
CHANNEL_NAME = 'advent-of-code'
players_cache = ()

intents = discord.Intents.default()
intents.message_content = True

def get_players():
    global players_cache
    now = time.time()
    debug_msg = 'Got Leaderboard From Cache'

    if not players_cache or (now - players_cache[0]) > (60 * POLL_MINS):
        debug_msg = 'Got Leaderboard Fresh'

        req = urllib.request.Request(URL)
        req.add_header('Cookie', 'session=' + COOKIE)
        page = urllib.request.urlopen(req).read()

        data = json.loads(page)
        players = [(member['name'],
                    member['local_score'],
                    member['stars'],
                    int(member['last_star_ts']),
                    member['completion_day_level'],
                    member['id']) for member in data['members'].values()]

        for i, player in enumerate(players):
            if not player[0]:
                anon_name = "anon #" + player[5]
                players[i] = (anon_name, player[1], player[2], player[3], player[4], player[5])

        players.sort(key=lambda tup: tup[3])
        players.sort(key=lambda tup: tup[2], reverse=True)
        players.sort(key=lambda tup: tup[1], reverse=True)
        players_cache = (now, players)

    print(debug_msg)
    return players_cache[1]

async def output_leaderboard(context, leaderboard_lst):
    item_len = len(leaderboard_lst[0])
    block_size = MAX_MESSAGE_LEN // item_len

    tmp_leaderboard = leaderboard_lst

    while (len(tmp_leaderboard) * item_len) > MAX_MESSAGE_LEN:
        output_str = '```'
        output_str += ''.join(tmp_leaderboard[:block_size])
        output_str += '```'
        await context.followup.send(output_str)
        tmp_leaderboard = tmp_leaderboard[block_size:]
    output_str = '```'
    output_str += ''.join(tmp_leaderboard)
    output_str += '```'
    await context.followup.send(output_str)

class AoCBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            application_id=os.getenv('DISCORD_CLIENT_ID')
        )
    
    async def setup_hook(self):
        await self.tree.sync()  # Sync slash commands with Discord
        print("Slash commands synced successfully!")
    
    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord and is in the following channels:')
        for guild in self.guilds:
            print('  ', guild.name)

# Create the bot using the new class
bot = AoCBot()

@bot.tree.command(name='leaderboard', description='Responds with the current leaderboard')
async def leaderboard(interaction: discord.Interaction, num_players: int = 20):
    if CHANNEL_NAME not in interaction.channel.name:
        return

    await interaction.response.defer()
    
    print('Leaderboard requested')
    players = get_players()[:num_players]

    max_name_len = len(max(players, key=lambda t: len(t[0]))[0])
    max_points_len = len(str(max(players, key=lambda t: t[1])[1]))
    max_stars_len = len(str(max(players, key=lambda t: t[2])[2]))

    leaderboard = []
    for i, player in enumerate(players):
        leaderboard.append(PLAYER_STR_FORMAT.format(rank=i + 1,
                                                    name=player[0], name_pad=max_name_len,
                                                    points=player[1], points_pad=max_points_len,
                                                    stars=player[2], stars_pad=max_stars_len,
                                                    star_time=time.strftime('%H:%M %d/%m', time.localtime(player[3]))))

    await output_leaderboard(interaction, leaderboard)

@bot.tree.command(name='rank', description='Responds with the current ranking of the supplied player')
async def rank(interaction: discord.Interaction, player_name: str):
    if CHANNEL_NAME not in interaction.channel.name:
        return

    await interaction.response.defer()
    
    print('Rank requested for: ', player_name)
    players = get_players()

    players = [(i, player) for i, player in enumerate(players) if player[0].upper() == player_name.upper()]
    if players:
        i, player = players[0]
        result = '```'
        result += PLAYER_STR_FORMAT.format(rank=i + 1,
                                            name=player[0], name_pad=len(player[0]),
                                            points=player[1], points_pad=len(str(player[1])),
                                            stars=player[2], stars_pad=len(str(player[2])),
                                            star_time=time.strftime('%H:%M %d/%m', time.localtime(player[3])))
        result += '```'
    else:
        result = 'Whoops, it looks like I can\'t find that player, are you sure they\'re playing?'
    await interaction.followup.send(result)

@bot.tree.command(name='keen', description="Responds with today's keenest bean")
async def keen(interaction: discord.Interaction):
    if CHANNEL_NAME not in interaction.channel.name:
        return
        
    await interaction.response.defer()
    
    print('Keenest bean requested')

    all_players = get_players()
    max_stars = max(all_players, key=lambda t: t[2])[2]
    players = [(i, player) for i, player in enumerate(all_players) if player[2] == max_stars]

    i, player = min(players, key=lambda t: t[1][3])

    result = 'Today\'s keenest bean is:\n```'
    result += PLAYER_STR_FORMAT.format(rank=i + 1,
                                        name=player[0], name_pad=len(player[0]),
                                        points=player[1], points_pad=len(str(player[1])),
                                        stars=player[2], stars_pad=len(str(player[2])),
                                        star_time=time.strftime('%H:%M %d/%m', time.localtime(player[3])))
    result += '```'
    await interaction.followup.send(result)

@bot.tree.command(name='daily', description='Will give the daily leaderboard for specified day')
async def daily(interaction: discord.Interaction, day: str = None):
    if CHANNEL_NAME not in interaction.channel.name:
        return

    await interaction.response.defer()
    
    if day is None:
        day = str((datetime.datetime.today() - datetime.timedelta(hours=5)).day)

    print("Daily leaderboard requested for day:", day)
    players = get_players()

    players_day = [player for player in players if day in player[4]]

    first_star = []
    second_star = []

    for player_day in players_day:
        if '1' in player_day[4][day]:
            first_star.append((player_day[0], int(player_day[4][day]['1']['get_star_ts'])))
        if '2' in player_day[4][day]:
            second_star.append((player_day[0], int(player_day[4][day]['2']['get_star_ts'])))

    first_star.sort(key=lambda data: data[1])
    second_star.sort(key=lambda data: data[1])

    final_table = []

    for i, player in enumerate(first_star):
        final_table.append((player[0], (len(players) - i), player[1], 1))

    for i, player in enumerate(second_star):
        index = [i for i, item in enumerate(final_table) if item[0] == player[0]][0]
        to_change = final_table[index]
        final_table[index] = (to_change[0], (to_change[1] + (len(players) - i)), player[1], 2)

    final_table.sort(key=lambda data: data[2])
    final_table.sort(reverse=True, key=lambda data: data[1])

    if not final_table:
        result = "```No Scores for this day yet```"
        await interaction.followup.send(result)
    else:
        max_name_len = len(max(final_table, key=lambda t: len(t[0]))[0])
        max_points_len = len(str(max(final_table, key=lambda t: t[1])[1]))
        max_stars_len = len(str(max(final_table, key=lambda t: t[3])[3]))
        leaderboard = []
        for place, player in enumerate(final_table):
            leaderboard.append(PLAYER_STR_FORMAT.format(rank=place + 1,
                                                        name=player[0], name_pad=max_name_len,
                                                        points=player[1], points_pad=max_points_len,
                                                        stars=player[3], stars_pad=max_stars_len,
                                                        star_time=time.strftime('%H:%M %d/%m', time.localtime(player[2]))))
        await output_leaderboard(interaction, leaderboard)

@bot.tree.command(name='remind', description='Mentions everyone with a reminder for the next Advent of Code challenge')
async def remind(interaction: discord.Interaction):
    if CHANNEL_NAME not in interaction.channel.name:
        return
    
    await interaction.response.defer()

    now = datetime.datetime.utcnow()
    next_challenge_time = (now + datetime.timedelta(days=1)).replace(hour=5, minute=0, second=0, microsecond=0)
    if now.hour >= 5:
        next_challenge_time += datetime.timedelta(days=1)

    time_diff = next_challenge_time - now
    remind_time = f"The next Advent of Code challenge is in {time_diff.days} days and {time_diff.seconds // 3600} hours and {(time_diff.seconds // 60) % 60} minutes."

    await interaction.followup.send(remind_time)

@bot.tree.command(name='join', description='Provides the Advent of Code login page and the private leaderboard code')
async def join(interaction: discord.Interaction):
    if CHANNEL_NAME not in interaction.channel.name:
        return
    
    await interaction.response.defer()

    login_url = "https://adventofcode.com/2024/auth/login"
    leaderboard_code = LEADERBOARD

    await interaction.followup.send(
        f"🌟 Join our Advent of Code fun! 🌟\n"
        f"Login here: {login_url}\n"
        f"Use this private leaderboard code: {leaderboard_code}\n"
        f"Let's see who wins!!"
    )

bot.run(TOKEN)