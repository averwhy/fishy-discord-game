import aiosqlite

class player:
    def __init__(self, bot, data):
        self.bot = bot
    async def get_trophy(self,data):
        trophyoid = data[4]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(trophyoid,))
            returndata = await c.fetchone()
            await db.commit()
        return returndata
    def get_caughtfish(self,data):
        fishescaught = data[2]
        return fishescaught
    def get_level(self,data):
        x = float(data[3])
        usermath = divmod(x,1)
        userlevel = usermath[0]
        return userlevel
    def get_xp(self,data):
        xpmath = divmod(data[3],1)
        userxp = xpmath[1]
        return userxp
    def get_guild_obj(self,data):
        guildid = data[6]
        guildobj = bot.get_guild(guildid)
        return guildobj
    def get_review_id(self,data):
        reviewid = data[8]
        return reviewid
    ##Now for updates n stuff
    async def update_caught_fish(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM f_users WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            await db.commit()
        async with aiosqlite.connect('fishypy.db') as db:
            await db.execute("Update f_users set totalcaught = (totalcaught + 1) where userid = ?",(userobject.id,))
            await db.commit()   
        return
    async def check_trophy(self,data,caughtoid):
        usersid = data[0]
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(caughtoid,))
            data2 = await c.fetchone()
            c = await db.execute("SELECT * FROM fishes WHERE oid = ?",(data[4],))
            data = await c.fetchone()
            await db.commit()
        try:
            FishLengthFromTrophy = data[4]
            FishLengthJustCaught = data2[4]
            if float(FishLengthFromTrophy) < float(FishLengthJustCaught):
                async with aiosqlite.connect('fishypy.db') as db:
                    await db.execute("Update f_users set trophyoid = ? where userid = ?", (caughtoid, usersid,))
                    await db.commit()
                return
            else:
                #No updating needed
                return
        except:
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("Update f_users set trophyoid = ? where userid = ?",(caughtoid,usersid,))
                await db.commit()
            print("user didnt have trophy so they got one")
            return
    async def add_user(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM f_users WHERE userid = ?",(userobject.name,))
            data = await c.fetchone()
            await db.commit()
            try:
                async with aiosqlite.connect('fishypy.db') as db:
                    #(userid integer, name text, totalcaught integer, Level real, trophyoid text, guildid integer, hexcolor text, reviewmsgid integer, commoncaught integer, uncommoncaught integer, rarecaught integer, legendarycaught integer, mythicalcaught integer)
                    await db.execute("INSERT INTO f_users VALUES (?,?,0,0.0,'None',?,'005dff', 0, 0, 0, 0, 0, 0)",(userobject.id,userobject.name,userobject.guild.id,))
                    await db.commit()
                return (f"`Done! Start fishing with {bot.defaultprefix}fish, or view your profile with {bot.defaultprefix}profile`")
            except Exception as e:
                return (f"`Something went wrong:` ```\n{e}\n```")
    async def update_review(self,userobject,reviewtext):
        try:
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("SELECT * FROM f_users WHERE userid = ?",(userobject.id,))
                data = await c.fetchone()
                await db.commit()
                
            if data is not None: # player exists
                stored_id = int(data[7])
                reviewchannel = bot.get_channel(735206051703423036)
                if reviewchannel is None:
                    reviewchannel = await bot.fetch_channel(735206051703423036)
                if stored_id != 0: # they have a review
                    msgtoedit = await reviewchannel.fetch_message(stored_id)
                    await msgtoedit.edit(content=f"Heres a review from {str(userobject)} ({userobject.id}):```\n{reviewtext}```")
                    return ("`Success! You've edited your review.")
                else: # they dont have a review
                    thereview = await reviewchannel.send(f"Heres a review from {userobject.mention} ({userobject.id}):```\n{reviewtext}```")
                    async with aiosqlite.connect('fishypy.db') as db:
                        await db.execute("Update f_users set reviewmsgid = ? where userid = ?",(thereview.id,userobject.id,))
                        await db.commit()
                        
                    return ("`Success! You can edit your review at any time using this command.`")
            else:
                return (f"`I was unable to retrieve your profile. Have you done {bot.defaultprefix}start yet?`")
        except Exception as e:
            return (f"`{e}`")
    async def update_guild(self,userid,newguildid):
        try:
            async with aiosqlite.connect('fishypy.db') as db:
                await db.execute("UPDATE f_users SET guildid = ? WHERE userid = ?",(userid,newguildid,))
                await db.commit()
            return
        except Exception as e:
            return e
    async def db_ban(self,userobject,reason):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM f_users WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            await db.execute("INSERT INTO bannedusers VALUES (?,?,?)",(userobject.id,userobject.name,reason,))
            await db.commit()
        return
    async def db_unban(self,userobject):
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM f_users WHERE userid = ?",(userobject.id,))
            data = await c.fetchone()
            if data is not None:
                await db.execute("DELETE FROM bannedusers WHERE userid = ?",(userobject.id,))
                await db.commit()
    async def update_xp(self, userobject, rarity): # this entire method is a mess, i hate it lmao
        rarity = float(rarity)
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("SELECT * FROM f_users WHERE userid = ?",(userobject.id,))
            data = await c.fetchone() 
        theirlevel = float(data[3])
        theirlevel2 = divmod(float(data[3]),1)
        updatevalue = round(float(rarity),3) #rounds xp
        oldlevel = theirlevel2[0] #the level only, since divmod returns a tuple
        oldxp = theirlevel2[1]
        ##################################
        xptoadd = updatevalue / 100
        xptoadd = xptoadd * bot.xp_multiplier
        bot.xpgainedinsession += xptoadd
        updatevalue = theirlevel + xptoadd
        newlevel = divmod(float(updatevalue),1)
        newlevelint = int(newlevel[0])
        async with aiosqlite.connect('fishypy.db') as db:
            c = await db.execute("UPDATE f_users SET Level = ? WHERE userid = ?",(updatevalue,userobject.id,))
            await db.commit()
        if newlevelint > int(oldlevel):
            return True
        else:
            return False
    async def update_profilecolor(self,hexstring,id):
        async with aiosqlite.connect('fishypy.db') as db:
            await db.execute("UPDATE f_users SET hexcolor = ? WHERE userid = ?",(hexstring,id,))
            await db.commit()
        return
    async def update_rarity_count(self,userobject,rarity):
        raritycalc2 = None
        rarity = rarity.strip()
        if rarity == "Common":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE f_users SET commoncaught = (commoncaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Mythical":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE f_users SET mythicalcaught = (mythicalcaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Legendary":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE f_users SET legendarycaught = (legendarycaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Rare":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE f_users SET rarecaught = (rarecaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        elif rarity == "Uncommon":
            async with aiosqlite.connect('fishypy.db') as db:
                c = await db.execute("UPDATE f_users SET uncommoncaught = (uncommoncaught + 1) WHERE userid = ?",(userobject.id,))
                await db.commit()
        else:
            print("Sadge")