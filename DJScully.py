#!/usr/bin/python
# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
import praw
import os
import re
from config_bot import *
from discord.ext import commands

TOKEN = 'MzY5OTg3NjkzOTg5NTkzMDk4.DbP--A.BPAwiSt0NvkMSxfEOmdvVWCkSzc'
score_limit = SCORE_LIMIT
bot = commands.Bot(command_prefix='&')
regex = re.compile(r"(?i)\bfree\b", re.IGNORECASE)


@bot.command()
async def hello(ctx):
    print("command hello runs")
    if ctx.author == bot.user:
        return

    msg = 'Hello {0.author.mention}'.format(ctx)
    await ctx.send(msg)


@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await bot.send_message(message.channel, msg)

    if message.content.startswith('!server_name'):
        servers = []
        msg = ''
        for server in bot.servers:
            servers.append(server)
            msg = 'This server is named: ' + server.name
        print(servers)
        await bot.send_message(message.channel, msg)

    if message.content.startswith('!test'):
        for server in bot.servers:
            # Spin through every server
            for channel in server.channels:
                # Channels on the server
                if channel.permissions_for(server.me).send_messages:
                    await bot.send_message(channel, "https://static12.insales.ru/images/products/1/7809/237185/original/believe.jpg")
                    # So that we don't send to every channel:
                    break

    if message.content.startswith('!join'):
        author_id = message.author.id
        # authorChannel = message.author.voice_channel
        # print(authorChannel.name)
        channels = bot.get_all_channels()
        msg = 'Authors id is ' + author_id

        for member in bot.get_all_members():
            if member.id == author_id:
                print("Im joining your channel " + member.name)

        for channel in channels:
            if channel.voice_members is not None:
                for member in channel.voice_members:
                    if member.id == author_id:
                        await bot.join_voice_channel(channel)

        await bot.send_message(message.channel, msg)

    if message.content.startswith('!leave'):
        for voice in bot.voice_clients:
            await voice.disconnect()

    if message.content.startswith('!channel_ID_list'):
        channels = bot.get_all_channels()
        channel_ids = []
        for channel in channels:
            print(channel.id)
            channel_ids.append(channel.id)

        await bot.send_message(message.channel, channel_ids)


async def send_message(title, url):
    print("this runs")
    for server in bot.servers:
        # Spin through every server
        for channel in server.channels:
            # Channels on the server
            if channel.permissions_for(server.me).send_messages:
                print("channel:" + str(channel))
                message = '---------------------------------------------------------------\n' \
                          + str(title) \
                          + '\n---------------------------------------------------------------\n' \
                          + str(url)
                await bot.send_message(channel, message)
                # So that we don't send to every channel:
                break


def login():
    """Logins to reddit, returns praw.reddit"""
    if not os.path.isfile("config_bot.py"):
        print("user config missing")
        exit(1)

    user_agent = "Game Deal Checker 1.0"
    r = praw.Reddit(user_agent=user_agent)
    r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)
    return r


async def run(r, posts):
    """Body function"""
    if not os.path.isfile("posts_checked.txt"):
        posts_checked = []
        print("wrong path for posts checked!")

    else:
        with open("posts_checked.txt", "r") as f:
            print("opened posts_checked.txt file!")
            posts_checked = f.read()
            posts_checked = posts_checked.split("\n")
            posts_checked = list(filter(None, posts_checked))

    subreddit = r.get_subreddit('GameDeals')
    print('Hot posts:' + str(sum(1 for _ in subreddit.get_hot(limit=posts))))
    for submission in subreddit.get_hot(limit=posts):
        if submission.id not in posts_checked:
            print('Submission score: ' + str(submission.score))
            if len(regex.findall(submission.title)) > 0:
                print('Adding: ' + str(submission.title))
                posts_checked.append(submission.id)
                if submission.title:
                    title = str(submission.title.encode('utf-8'))
                if submission.url:
                    url = str(submission.url.encode('utf-8'))
                print(title)
                print(url)
                await send_message(title=submission.title, url=submission.url)

    with open("posts_checked.txt", "w") as f:
        print("Writing to posts_checked.txt!")
        for post_id in posts_checked:
            f.write(post_id + "\n")


async def scrape_subreddit():
    await run(login(), POST_LIMIT)


@bot.event
async def on_ready():
    """Start of bot"""
    print('Logged in discord as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    print("running scrape on r/GameDeals")
    await run(login(), POST_LIMIT)

bot.run(TOKEN)
