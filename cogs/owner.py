import discord
import platform
import time
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import asyncio
import aiosqlite
from datetime import datetime
OWNER_ID = 267410788996743168

class devtools(commands.Cog, command_attrs=dict(hidden=True)):
    """
    Tools for the developer
    """
    def __init__(self,bot):
        self.bot = bot
    
    async def cog_check(self,ctx):
        return ctx.author.id == OWNER_ID
        
    @tasks.loop(minutes=10)
    async def database_backup_task(self):
        try:
            await self.bot.db.commit()
            self.bot.backup_db = await aiosqlite.connect('fpy_backup.db')
            await self.bot.db.backup(self.bot.backup_db)
            await self.bot.backup_db.commit()
            await self.bot.backup_db.close()
            return
        except Exception as e:
            print(f"An error occured while backing up the database:\n`{e}`")
            return
    
    @commands.group(invoke_without_command=True,hidden=True)
    async def dev(self, ctx):
        #bot dev commands
        await ctx.send("`You're missing one of the below arguements:` ```md\n- reload\n- loadall\n- status <reason>\n- ban <user> <reason>\n```")

    @dev.command(aliases=["r","reloadall"])
    async def reload(self, ctx):
        output = ""
        amount_reloaded = 0
        async with ctx.channel.typing():
            for e in self.bot.initial_extensions:
                try:
                    self.bot.reload_extension(e)
                    amount_reloaded += 1
                except Exception as e:
                    e = str(e)
                    output = output + e + "\n"
            await asyncio.sleep(1)
            if output == "":
                await ctx.send(content=f"`{len(self.bot.initial_extensions)} cogs succesfully reloaded.`") # no output = no error
            else:
                await ctx.send(content=f"`{amount_reloaded} cogs were reloaded, except:` ```\n{output}```") # output

    @dev.command(aliases=["load","l"])
    async def loadall(self, ctx):
        output = ""
        amount_loaded = 0
        async with ctx.channel.typing():
            for e in self.bot.initial_extensions:
                try:
                    self.bot.load_extension(e)
                    amount_loaded += 1
                except Exception as e:
                    e = str(e)
                    output = output + e + "\n"
            await asyncio.sleep(1)
            if output == "":
                await ctx.send(content=f"`{len(self.bot.initial_extensions)} cogs succesfully loaded.`") # no output = no error
            else:
                await ctx.send(content=f"`{amount_loaded} cogs were loaded, except:` ```\n{output}```") # output

    @dev.command()
    async def status(self, ctx, *, text):
        # Setting `Playing ` status
        if text is None:
            await ctx.send(f"{ctx.guild.me.status}")
        if len(text) > 60:
            await ctx.send("`Too long you pepega`")
            return
        try:
            await self.bot.change_presence(activity=discord.Game(name=text))
            await ctx.message.add_reaction("\U00002705")
        except Exception as e:
            await ctx.message.add_reaction("\U0000274c")
            await ctx.send(f"`{e}`")
    
    @dev.command(aliases=['nick','n'])
    async def nickname(self, ctx, *, text):
        try:
            await ctx.guild.me.edit(nick=text, reason=f"My developer {ctx.author} requested this change")
        except:
            return await ctx.send_in_codeblock("Done", language='css')

    @dev.command()
    async def stop(self, ctx):
        askmessage = await ctx.send("`you sure?`")
        def check(m):
            newcontent = m.content.lower()
            return newcontent == 'yea' and m.channel == ctx.channel and m.author.id == OWNER_ID
        try:
            await self.bot.wait_for('message', timeout=5, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Timed out. haha why didnt you respond you idiot`")
        else:
            await ctx.send("`bye`")
            print(f"Bot is being stopped by {ctx.message.author} ({ctx.message.id})")
            await self.bot.db.commit()
            await self.bot.db.close()
            await self.bot.logout()
        
    @dev.command()
    async def sql(self, ctx, *, statement):
        try:
            cur = await bot.db.execute(statement)
            
            
            
    @dev.group(invoke_without_command=True)
    async def eco(self, ctx):
        pass
    
    @eco.command()
    async def reset(self, ctx, user: discord.User = None):
        if user is None:
            await ctx.send("Provide an user")
            return
        player = await self.bot.get_player(user.id)
        if player is None:
            await ctx.send("They're not even in the database...")
            return
        
        await self.bot.db.execute("UPDATE e_users SET bal = 100 WHERE id = ?",(user.id,))
        await ctx.send("Reset.")
        
    @eco.command()
    async def give(self, ctx, user: discord.User, amount):
        amount = float(amount)
        player = await self.bot.get_player(user.id)
        if player is None:
            await ctx.send("They're not even in the database...")
            return
        
        await self.bot.db.execute("UPDATE e_users SET bal = (bal + ?) WHERE id = ?",(amount, user.id,))
        await ctx.send(f"Success.\nNew balance: ${(player[3] + amount)}")
    
    @eco.command(name="set")
    async def setamount(self, ctx, user: discord.User = None, amount: float = None):
        if user is None:
            await ctx.send("Provide an user.")
            return
        if amount is None:
            await ctx.send("Provide an amount.")
        player = await self.bot.get_player(user.id)
        if player is None:
            await ctx.send("They're not even in the database...")
            return
        
        await self.bot.db.execute("UPDATE e_users SET bal = ? WHERE id = ?",(amount, user.id,))
        await ctx.send("Success.")
        
    @dev.command(aliases=["bu"])
    async def backup(self, ctx):
        try:
            await self.bot.db.commit()
            self.bot.backup_db = await aiosqlite.connect('ecox_backup.db')
            await self.bot.db.backup(self.bot.backup_db)
            await self.bot.backup_db.commit()
            await self.bot.backup_db.close()
            await ctx.send("done, lol")
            return
        except Exception as e:
            await ctx.send(f"An error occured while backing up the database:\n`{e}`")
            return
        
    @dev.command(hidden=True,name="stream")
    async def streamingstatus(self, ctx, *, name):
        if ctx.author.id != 267410788996743168:
            return
        await self.bot.change_presence(activity=discord.Streaming(name=name,url="https://twitch.tv/monstercat/"))
        await ctx.send("aight, done")
        
    @dev.command()
    async def m(self, ctx):
        if self.bot.maintenance:
            self.bot.maintenance = False
            return await ctx.send("Maintenence is now off.")
        else:
            self.bot.maintenance = True
            return await ctx.send("Maintenence is now on.")
def setup(bot):
    bot.add_cog(devtools(bot))