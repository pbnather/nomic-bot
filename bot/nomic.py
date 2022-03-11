# nomic.py
# author: pbnather, michsok
import os
from discord import Embed
from discord.ext import commands
from dotenv import load_dotenv
from gitlab_api import GitlabAPI

load_dotenv()

player_ids = os.getenv("PLAYER_IDS").split(",")
players = []
guild = None
current_player = int(os.getenv("STARTING_PLAYER"))
gitlab_api = GitlabAPI()

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    guild_id = os.getenv("GUILD_ID")
    guild = bot.get_guild(int(guild_id))
    for id in player_ids:
        players.append(await guild.fetch_member(int(id)))
    print("Bot is up and running!")
    print(f'Players: {[player.display_name for player in players]}')


def only_current_player():
    async def predicate(ctx):
        return ctx.author == players[current_player]
    return commands.check(predicate)


def only_players():
    async def predicate(ctx):
        return ctx.author in players
    return commands.check(predicate)


@bot.command(name='ping', brief="Ping current player")
async def show_State(ctx):

    response = f'Now is {players[current_player].display_name} turn'

    await ctx.send(response)


@bot.command(name='pass', brief="Pass turn to next player")
@only_current_player()
async def pass_turn(ctx):
    global current_player
    current_player = (current_player + 1) % len(players)

    response = f'Now is {players[current_player].mention} turn'

    await ctx.send(response)


@bot.command(name='rule', brief="Show rule content")
async def print_rule(ctx, id: int):

    embed = gitlab_api.print_rule(rule_number=id)

    await ctx.send(embed=embed)


@bot.command(name='const', brief="Show const rules")
async def print_rule(ctx):

    embed = gitlab_api.print_rules(rule_type='const')

    await ctx.send(embed=embed)


@bot.command(name='rules', brief="Show not-const rules")
async def print_rule(ctx):

    embed = gitlab_api.print_rules(rule_type='not-const')

    await ctx.send(embed=embed)


@bot.command(name='all', brief="Show all rules")
async def print_rule(ctx):

    const_embed = gitlab_api.print_rules(rule_type='const')
    rules_embed = gitlab_api.print_rules(rule_type='not-const')

    await ctx.send(embed=const_embed)
    await ctx.send(embed=rules_embed)


@bot.command(name="add")
@only_current_player()
async def new_rule(ctx):

    rule_content = list(
        ' '.join((ctx.message.content.split(' ')[1:])).split('\n'))

    embed = gitlab_api.add_rule(
        player_name=ctx.author.display_name,
        rule_content=rule_content
    )
    await ctx.send(embed=embed)


@bot.command(name="edit")
@only_current_player()
async def edit_rule(ctx, id: int):

    rule_content = str(id) + '. \n' + \
        ' '.join(ctx.message.content.split(' ')[2:])
    rule_content = rule_content.split('\n')

    embed = gitlab_api.edit_rule(
        player_name=ctx.author.display_name,
        rule_id=id,
        rule_content=rule_content
    )
    await ctx.send(embed=embed)


@bot.command(name="transmute")
@only_current_player()
async def transmute_rule(ctx, id: int):

    embed = gitlab_api.transmute_rule(
        player_name=ctx.author.display_name,
        rule_id=id
    )
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('It\'s not your turn')
        return
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send('Not valid argument')
        return


# Starting the bot
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
