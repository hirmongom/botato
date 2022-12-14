from discord.ext import commands
from random import choice

from modules.misc.functions import *

class Misc(commands.Cog, name="Miscellaneous"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command(name = "ping", help= "Returns Pong")
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong")


    @commands.command(name = 'github', help = 'My github profile')
    async def github(self, ctx: commands.Context):
        await ctx.send('https://github.com/HiramMontejano')


    @commands.command(name = 'phasmo_role', help = 'Sends a role in private to every user in your voice channel', aliases = ["pr"])
    async def give_role(self, ctx: commands.Context):
        if not authorInVoiceChannel(ctx):
            return await ctx.send('You need to be in a voice channel to use this command!')

        voice_channel = ctx.message.author.voice.channel

        for member in voice_channel.members:
            curr_role = get_role()
            await member.send(curr_role)
            if curr_role[:2] == '42':
                count = 1
                while (count < 3):
                    curr_role = get_role()
                    await member.send(curr_role)
                    if curr_role[:2] == '42':
                        count = 0
                    count += 1

        await ctx.send('Roles have been given, have fun!')


    @commands.command(name = 'phasmongus', help = 'Chooses a random user in your voice channel as impostor. The chosen one will receive a message in private notifying him')
    async def choose_impostor(self, ctx: commands.Context):
        if not authorInVoiceChannel(ctx):
            return await ctx.send('You need to be in a voice channel to use this command!')

        voice_channel = ctx.author.voice.channel
        members = []

        for member in voice_channel.members:
            members.append(member)

        impostor = choice(members)
        await impostor.send("You are the impostor, ruin the game")

        await ctx.send('There is an impostor in your game, be careful!')


    @commands.command(name = 'chooseforme', help = 'Chooses an item from a set of items (item1, item2, item3, ...)')
    async def choose(self, ctx: commands.Context, *item_list):

        item_list = ' '.join(item_list)
        splitted_list = [x.strip() for x in item_list.split(',')]

        await ctx.send(choice(splitted_list))


    @commands.command(name = 'to_do', help= 'Things I plan on implementing')
    async def todo(self, ctx: commands.Context):
        todo_list = [
        "No new ideas yet"]

        cnt = 1;
        for item in todo_list:
            await ctx.send(f'{cnt} >> {item}')
            cnt += 1


def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))