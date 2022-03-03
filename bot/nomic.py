# nomic.py
# author: pbnather
import os
import re
import urllib.request
from discord import Embed
from discord.ext import commands
from dotenv import load_dotenv

rules = {}


def isRule(input):
    pattern = re.compile(r"[0-9]+.")
    is_rule = pattern.match(input, re.IGNORECASE)
    return (is_rule, "`konst`" in input)


def parse_rules():
    with urllib.request.urlopen(
        "https://gitlab.com/michsok/nomic/-/raw/main/README.md"
    ) as f:
        rule_started = False
        rule_content = []
        rule_number = ""
        for line in f.readlines():
            line = line.decode("utf-8")
            (is_rule, _) = isRule(line)
            if "## Zasady pozakonstytucyjne" in line:
                continue
            if is_rule:
                if rule_started:
                    rules[rule_number] = rule_content
                    rule_content = []
                    rule_number = ""
                rule_started = True
                rule_content.append(line)
                rule_number = line.split(".")[0]
            elif rule_started:
                rule_content.append(line)
        rules[rule_number] = rule_content


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")


def create_embed(const, embed):
    for rule in rules.keys():
        if const:
            if "`konst`" not in rules[rule][0]:
                continue
        else:
            if "`konst`" in rules[rule][0]:
                continue
        content = ""
        for line in rules[rule][1:]:
            content += line
        embed.add_field(
            name=rules[rule][0].replace("\n", ""),
            value=content + "\n ",
            inline=False,
        )


@bot.command(name="rule", brief="Shows rule content")
async def show_rule(ctx, number: str):
    if number in rules:
        embed = Embed(
            title=rules[number][0].replace("\n", ""),
            color=0x16D3D3 if "`konst`" in rules[number][0] else 0xFB8B40,
        )
        content = ""
        for line in rules[number][1:]:
            content += line
        embed.description = content
        await ctx.send(embed=embed)
    else:
        response = "Nie ma takiej zasady"
        await ctx.send(response)


@bot.command(name="const", brief="Shows all const rules")
async def show_rule(ctx):
    embed = Embed(
        title="Zasady konstytucyjne",
        color=0x16D3D3,
    )
    create_embed(True, embed=embed)
    await ctx.send(embed=embed)


@bot.command(name="rules", brief="Shows all no-const rules")
async def show_rule(ctx):
    embed = Embed(
        title="Zasady pozakonstytucyjne",
        color=0xFB8B40,
    )
    create_embed(False, embed=embed)
    await ctx.send(embed=embed)


@bot.command(name="update", brief="Updates rules from Gitlab")
async def update_rules(ctx):
    parse_rules()
    response = "Rules updated"
    await ctx.send(response)


parse_rules()
bot.run(TOKEN)
