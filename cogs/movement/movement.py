import discord
from discord.ext import commands
from copy import deepcopy
import asyncio
from io import BytesIO
from cogs.movement.context import Context
from cogs.movement.player import Player
from cogs.movement.playerY import PlayerY
from cogs.movement.parsers import execute_string
from cogs.movement.utils import SimError, SimNode


async def setup(bot):
    bot.env = {}

    await bot.add_cog(Movement(bot))

class Movement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.msg_links = {}

    def sim(self, context: Context, input: str):

        execute_string(context, input)
        
        return context
    
    async def generic_sim(self, dpy_ctx: commands.Context, input, continuation = None, edit = None, history = False, *, color_output = True, sim_type = "xz"):
        
        if sim_type == "y":
            context = Context(PlayerY(), [self.bot.env], self.bot.params['is_dev'], sim_type)
        elif sim_type == "xz":
            context = Context(Player(), [self.bot.env], self.bot.params['is_dev'], sim_type)
            

        if continuation:
            parent = self.msg_links[continuation]
            context.player = deepcopy(parent.player)
        
        errored = True
        try:
            task = asyncio.to_thread(self.sim, context, input)
            context = await asyncio.wait_for(task, timeout=self.bot.params['sim_timeout'])

            if history:
                results = context.history_string()
            elif color_output:
                results = context.result()
            else:
                results = context.result(backup=True)

            errored = False

        except asyncio.TimeoutError:
            results = 'Simulation timed out.'
        except SimError as e:
            results = str(e)
        except:
            if self.bot.params['is_dev']:
                raise
            results = 'Something went wrong.'

        if context.macro:
            if context.macro_format == 'mpk':
                buffer = BytesIO(context.macro_csv().encode('utf8'))
                kwargs = {'content': results, 'file': discord.File(fp=buffer, filename=f'{context.macro}.csv')}
            elif context.macro_format == 'cyv':
                buffer = BytesIO(context.macro_json().encode('utf8'))
                kwargs = {'content': results, 'file': discord.File(fp=buffer, filename=f'{context.macro}.json')}
        elif len(results) > 1990:
            if color_output:
                results = context.result(backup=True)
                if len(results) < 1990:
                    kwargs = {'content': results}
                else:
                    buffer = BytesIO(results.encode('utf8'))
                    kwargs = {'content': 'Uploaded output to file since output was too long.', 'file': discord.File(fp=buffer, filename='output.txt')}
            
            elif not color_output:
                buffer = BytesIO(results.encode('utf8'))
                kwargs = {'content': 'Uploaded output to file since output was too long.', 'file': discord.File(fp=buffer, filename='output.txt')}
                
        else:
            kwargs = {'content': results}

        ##### Test this function ##################
        # if context.adding_output:                 #
        #     context.adding_output = False         #
        #     kwargs['content'] = results + "\n```" #
        ##### Test this function ##################

        if errored:
            kwargs.pop('file', None)
        
        if edit:
            if 'file' in kwargs:
                kwargs['content'] = 'Cannot edit attachments.\n' + kwargs['content']
                kwargs.pop('file', None)
            await edit.botmsg.edit(**kwargs)
            self.msg_links[edit.msgid].player = deepcopy(context.player)
        else:
            botmsg = await dpy_ctx.channel.send(**kwargs)

            node = SimNode(dpy_ctx.message.id, botmsg, context.player)
            self.msg_links[dpy_ctx.message.id] = node
            if continuation:
                parent.children.append(dpy_ctx.message.id)
        
    @commands.command(aliases=['sim', 's'])
    async def simulate(self, ctx: commands.Context, *, text: str):
         await self.generic_sim(ctx, text)

    
    @commands.command(aliases=['ncsim', 'ncs', 'nsim', 'ns'])
    async def nocolor_simulate(self, ctx: commands.Context, *, text: str):
        await self.generic_sim(ctx, text, color_output=False)

    @commands.command(aliases=['his', 'h'])
    async def history(self, ctx: commands.Context, *, text: str):
        await self.generic_sim(ctx, text, history=True)
    
    @commands.command(aliases=['t'])
    async def then(self, ctx: commands.Context, *, text: str):
        if ctx.message.reference is None or ctx.message.reference.message_id not in self.msg_links:
            await ctx.send("You must reply to a simulation command")
            return
        
        srcid = ctx.message.reference.message_id
        await self.generic_sim(ctx, text, continuation = srcid)
    
    @commands.command(aliases=['th'])
    async def thenh(self, ctx: commands.Context, *, text: str):
        if ctx.message.reference is None or ctx.message.reference.message_id not in self.msg_links:
            await ctx.send("You must reply to a simulation command")
            return
        
        srcid = ctx.message.reference.message_id
        await self.generic_sim(ctx, text, continuation = srcid, history = True)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.id not in self.msg_links:
            return
        
        await self.edit_down(after.channel, after)
    
    async def edit_down(self, channel, msg):
        text = msg.content
        if any(text.startswith(cmd) for cmd in (';y', ';ysim')):
            sim_type = "y"
        else:
            sim_type = "xz"

        history = any(text.startswith(cmd) for cmd in (';history ', ';his ', ';h ', ';thenh ', ';th '))
        for i in range(len(text)):
            if text[i].isspace():
                text = text[i+1:]
                break

        if msg.reference:
            continuation = msg.reference.message_id
        else:
            continuation = None
        
        # This is only for xz movement
        await self.generic_sim(channel, text, history = history, edit = self.msg_links[msg.id], continuation = continuation, sim_type = sim_type)

        for child_id in self.msg_links[msg.id].children:
            child = await channel.fetch_message(child_id)
            await self.edit_down(channel, child)

    @commands.command(aliases=['ysim', 'y'])
    async def y_simulate(self, ctx: commands.Context, *, text: str):
        await self.generic_sim(ctx, text, sim_type="y")
    
    @commands.command(aliases=['yhis', 'yh'])
    async def y_history(self, ctx: commands.Context, *, text: str):
        await self.generic_sim(ctx, text, sim_type="y", history=True)
