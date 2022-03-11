# nomic.py
# author: pbnather, michsok
import os
from discord.ext import commands
from dotenv import load_dotenv
from gitlab_api import GitlabAPI

load_dotenv()

rules = {}
players = os.getenv("PLAYERS").split(",")
current_player = -1
gitlab_api = GitlabAPI()

bot = commands.Bot(command_prefix="!")


@bot.command(name='rule')
async def print_rule(ctx):
    print(ctx)
    try:
        rule_id = ctx.message.content.split()[1]
        rule_id = int(rule_id)
    except ValueError:
        response = f'{rule_id} is not a valid number.'
        await ctx.send(response)

    embed = gitlab_api.print_rule(
        rule_number=rule_id
    )

    await ctx.send(embed=embed)


@bot.command(name='const')
async def print_rule(ctx):

    embed = gitlab_api.print_rules(rule_type='const')

    await ctx.send(embed=embed)


@bot.command(name='rules')
async def print_rule(ctx):

    embed = gitlab_api.print_rules(rule_type='not-const')

    await ctx.send(embed=embed)


@bot.command(name='all')
async def print_rule(ctx):

    embed = gitlab_api.print_rules(rule_type='const')
    await ctx.send(embed=embed)
    embed = gitlab_api.print_rules(rule_type='not-const')
    await ctx.send(embed=embed)


@bot.command(name="add")
async def new_rule(ctx):
    rule_content = list(
        ' '.join((ctx.message.content.split(' ')[1:])).split('\n'))

    embed = gitlab_api.add_rule(
        player_name=ctx.author.display_name,
        rule_content=rule_content
    )
    await ctx.send(embed=embed)


@bot.command(name="edit")
async def edit_rule(ctx):
    try:
        rule_id = ctx.message.content.split()[1]
        rule_id = int(rule_id)
    except ValueError:
        response = f'{rule_id} is not a valid number.'
        await ctx.send(response)
    rule_content = str(rule_id) + '. ' + \
        ' '.join(ctx.message.content.split(' ')[2:])
    rule_content = rule_content.split('\n')

    embed = gitlab_api.edit_rule(
        player_name=ctx.author.display_name,
        rule_id=rule_id,
        rule_content=rule_content
    )
    await ctx.send(embed=embed)


@bot.command(name="transmute")
async def transmute_rule(ctx):
    try:
        rule_id = ctx.message.content.split()[1]
        rule_id = int(rule_id)
    except ValueError:
        response = f'{rule_id} is not a valid number.'
        await ctx.send(response)
    embed = gitlab_api.transmute_rule(
        player_name=ctx.author.display_name,
        rule_id=rule_id
    )
    await ctx.send(embed=embed)

# Starting the bot
print(f'Players: {players}')
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
