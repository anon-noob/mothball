import discord
from discord.ext import commands
import json
import os

class Mothball(commands.Bot):
    async def setup_hook(self):

        if os.path.isfile('restart.json'):
            with open('restart.json', 'r') as restart:
                info = json.load(restart)
                channel = await self.fetch_channel(info['channel'])
                msg = await channel.fetch_message(info['msg'])
                await msg.edit(content='Restarting...   Restarted!')
            os.remove('restart.json')
        
        await self.load_extension('cogs.admin')
        await self.load_extension('cogs.misc')
        await self.load_extension('cogs.movement.movement')
    
    async def on_message(self, msg: discord.Message):
        if msg.author.id in self.params['banned']:
            return
        elif isinstance(msg.channel, discord.DMChannel) and msg.author.id not in self.params['trusted']:
            return
        
        if msg.content.startswith(';;'):
            msg.content = msg.content[:2] + ' ' + msg.content[2:]

        await self.process_commands(msg)

def command_prefix(bot, msg: discord.Message):
    return bot.params['prefix']

intents = discord.Intents.all()
bot = Mothball(command_prefix=command_prefix, intents=intents, help_command=None)

@bot.command()
async def help(ctx):
    await ctx.send('Read the wiki!\n<https://github.com/anon-noob/mothball/wiki#welcome-to-the-mothball-wiki>\n(Original Mothball by CyrenArkade)')

@bot.command()
async def version(ctx):
    v = bot.params['version']
    s = f"""Mothball version {v}
Recent changes:
- A mini wiki has been created to document all simulation functions (type `;help`)
- Texts are now formatted so you can use curly braces to evaluate anything inside {'{}.'}
  - For example `outz(label=greater than {{0.0625-0.001}})` would result in `greater than 0.0615: 0`
- `var()` works properly now and converts to the appriopiate datatype instead of just a string
- More detailed error messages.
- **Bug Fix:** Expressions work inside `anglequeue` and `turnqueue`. Now you can do `aq(1, 1+1, 1+1+1)`.
- **Bonus Addon:** Multiplication is allowed (but not exponents).
"""
    await ctx.send(s)

if __name__ == '__main__':

    with open('params.json', 'r') as input:
        params = json.load(input)
    bot.params = params

    bot.run(bot.params['token'])
