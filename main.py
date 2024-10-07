import random
import asyncio
import discord
import json
import re
from discord import app_commands
from discord.ext import commands

# variables #

settingsFile = open('settings.json', 'r')
settings = json.load(settingsFile)
settingsFile.close()

profilesFile = open('profiles.json', 'r+')
data = json.load(profilesFile)

shopFile = open('shop.json', 'r+')
shopData = json.load(shopFile)

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# events #

@client.event
async def setup_hook():
    await tree.sync(guild=discord.Object(id=1201198351866142821))

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=''), status=discord.Status.online)
    print(f'{client.user} is ready!')
    
@client.event
async def on_member_join(member):
    try:
        role = member.guild.get_role(1201299282708410458)
        await member.add_roles(role)
    except Exception:
        print('wrong server')

# commands #

@tree.command(name='ping', description="Test bot's latency")
async def ping(interaction):
    await interaction.response.send_message(f'{round(client.latency, 3)} seconds')

@app_commands.choices(race=[
    app_commands.Choice(name="Human", value="Human"),
    app_commands.Choice(name="Elf", value="Elf"),
    app_commands.Choice(name="Fishman", value="Fishman"),
    app_commands.Choice(name="Cyborg", value="Cyborg")
])
@tree.command(name='createprofile', description="Create your profile")
async def createprofile(interaction, race: app_commands.Choice[str], name: str = None):
    embedFailed = discord.Embed(description="Profile already exists.", colour=discord.Colour.red())
    embedCreated = discord.Embed(description="Profile created.", colour=discord.Colour.green())
        
    if str(interaction.user.id) in data:
        await interaction.response.send_message(embed=embedFailed)
        return
        
    data[str(interaction.user.id)] = {}
    data[str(interaction.user.id)]["Health"] = 100
    data[str(interaction.user.id)]["Race"] = race.value
    data[str(interaction.user.id)]["Level"] = 1
    data[str(interaction.user.id)]["Points"] = 10
    data[str(interaction.user.id)]["Money"] = 0
    data[str(interaction.user.id)]["Attributes"] = {
        "Strength": 0,
        "Fortitude": 0,
        "Agility": 0,
        "Luck": 0
    }
    data[str(interaction.user.id)]["Inventory"] = []
    
    if race.value == "Human":
        data[str(interaction.user.id)]["Attributes"] = {
            "Strength": 0,
            "Fortitude": 1,
            "Agility": 0,
            "Luck": 2
        }
    elif race.value == "Elf":
        data[str(interaction.user.id)]["Attributes"] = {
            "Strength": 0,
            "Fortitude": 0,
            "Agility": 2,
            "Luck": 1
        }
    elif race.value == "Fishman":
        data[str(interaction.user.id)]["Attributes"] = {
            "Strength": 2,
            "Fortitude": 1,
            "Agility": 0,
            "Luck": 0
        }
    else:
        data[str(interaction.user.id)]["Attributes"] = {
            "Strength": 1,
            "Fortitude": 2,
            "Agility": 0,
            "Luck": 0
        }
            
    profilesFile.seek(0)
    json.dump(data, profilesFile, indent=2)
    profilesFile.truncate()
    
    try:
        await interaction.user.edit(nick=name)
    except Exception:
        print(f'Missing permissions to rename {interaction.user}')
        
    await interaction.response.send_message(embed=embedCreated)
    
    try:
        role = interaction.user.guild.get_role(1201304156795842661)
        role2 = interaction.user.guild.get_role(1201299282708410458)
        await interaction.user.remove_roles(role2)
        await interaction.user.add_roles(role)
    except Exception:
        print('wrong server')
    
@tree.command(name='attributes', description="Manage your stat points")
async def attributes(interaction, member: discord.Member = None):
    if not str(interaction.user.id) in data:
        embedFailed = discord.Embed(description="Profile doesn't exist.", colour=discord.Colour.red())
        await interaction.response.send_message(embed=embedFailed)
        return
    
    if member:
        userid = str(member.id)

        embed = discord.Embed(title=f"{member.display_name}\'s Attributes", description=f'Level: {data[userid]["Level"]}\nHe has {data[userid]["Points"]} points left to spend', colour=discord.Colour.random())
        embed.add_field(name='Strength', value=str({data[userid]["Attributes"]["Strength"]}), inline=False)
        embed.add_field(name='Fortitude', value=str({data[userid]["Attributes"]["Fortitude"]}), inline=False)
        embed.add_field(name='Agility', value=str({data[userid]["Attributes"]["Agility"]}), inline=False)
        embed.add_field(name='Luck', value=str({data[userid]["Attributes"]["Luck"]}), inline=False)
        embed.set_footer(text=f'{member.id}')
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
        return
    
    userid = str(interaction.user.id)
    
    embed = discord.Embed(title="Attributes", description=f'Level: {data[userid]["Level"]}\nYou have {data[userid]["Points"]} points left to spend', colour=discord.Colour.random())
    embed.add_field(name='Strength', value=str({data[userid]["Attributes"]["Strength"]}), inline=False)
    embed.add_field(name='Fortitude', value=str({data[userid]["Attributes"]["Fortitude"]}), inline=False)
    embed.add_field(name='Agility', value=str({data[userid]["Attributes"]["Agility"]}), inline=False)
    embed.add_field(name='Luck', value=str({data[userid]["Attributes"]["Luck"]}), inline=False)
    embed.set_footer(text=f'{interaction.user.id}')
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    
    StrengthButton = discord.ui.Button(style=discord.ButtonStyle.primary, label="Strength", custom_id="Strength", disabled=True if data[userid]["Points"] == 0 else False)
    FortitudeButton = discord.ui.Button(style=discord.ButtonStyle.primary, label="Fortitude", custom_id="Fortitude", disabled=True if data[userid]["Points"] == 0 else False)
    AgilityButton = discord.ui.Button(style=discord.ButtonStyle.primary, label="Agility", custom_id="Agility", disabled=True if data[userid]["Points"] == 0 else False)
    LuckButton = discord.ui.Button(style=discord.ButtonStyle.primary, label="Luck", custom_id="Luck", disabled=True if data[userid]["Points"] == 0 else False)
    resetButton = discord.ui.Button(style=discord.ButtonStyle.danger, label="Reset", disabled=not any(item == "Fruit" for item in data[userid]["Inventory"]))
    
    view = discord.ui.View()
    view.add_item(StrengthButton)
    view.add_item(FortitudeButton)
    view.add_item(AgilityButton)
    view.add_item(LuckButton)
    view.add_item(resetButton)
    
    await interaction.response.send_message(embed=embed, view=view)
    
    async def callback(callbackInteraction):
        if callbackInteraction.user.id != interaction.user.id:
            await callbackInteraction.response.send_message(f'You are not the author of this message.', ephemeral=True, delete_after=2)
            return
            
        if data[userid]["Points"] > 0:
            data[userid]["Attributes"][callbackInteraction.data["custom_id"]] += 1
            data[userid]["Points"] -= 1
            profilesFile.seek(0)
            json.dump(data, profilesFile, indent=2)
            profilesFile.truncate()
        
        await callbackInteraction.response.defer()
        msg = await interaction.original_response()
        
        StrengthButton.disabled = True if data[userid]["Points"] == 0 else False
        FortitudeButton.disabled = True if data[userid]["Points"] == 0 else False
        AgilityButton.disabled = True if data[userid]["Points"] == 0 else False
        LuckButton.disabled = True if data[userid]["Points"] == 0 else False
        
        embed.description = f'Level: {data[userid]["Level"]}\nYou have {data[userid]["Points"]} points left to spend'
        embed.set_field_at(index=0, name='Strength', value=str({data[userid]["Attributes"]["Strength"]}), inline=False)
        embed.set_field_at(index=1, name='Fortitude', value=str({data[userid]["Attributes"]["Fortitude"]}), inline=False)
        embed.set_field_at(index=2, name='Agility', value=str({data[userid]["Attributes"]["Agility"]}), inline=False)
        embed.set_field_at(index=3, name='Luck', value=str({data[userid]["Attributes"]["Luck"]}), inline=False)
        await msg.edit(embed=embed, view=view)
        
    global confirmation
    confirmation = 0
        
    async def reset(callbackInteraction):
        if callbackInteraction.user.id != interaction.user.id:
            await callbackInteraction.response.send_message(f'You are not the author of this message.', ephemeral=True, delete_after=2)
            return
        
        global confirmation
        for item in data[userid]["Inventory"]:
            if item == "Fruit":
                confirmation += 1
        
        msg = await interaction.original_response()
                
        if confirmation == 1:
            resetButton.label = "Are You Sure"
            await callbackInteraction.response.defer(ephemeral=True)
            await msg.edit(embed=embed, view=view)
            
        if confirmation == 2:
            resetButton.label = "Reseting.."
            await callbackInteraction.response.defer(ephemeral=True, thinking=True)
            await msg.edit(embed=embed, view=view)
            
            for item in data[userid]["Inventory"]:
                if item == "Fruit":
                    data[userid]["Inventory"].remove(item)
            
            data[userid]["Attributes"] = {
                "Strength" : 0,
                "Fortitude": 0,
                "Agility": 0,
                "Luck": 0
            }
            
            if data[userid]["Race"] == "Human":
                data[userid]["Attributes"]["Luck"] = 2
                data[userid]["Attributes"]["Fortitude"] = 1
            elif data[userid]["Race"] == "Elf":
                data[userid]["Attributes"]["Agility"] = 2
                data[userid]["Attributes"]["Luck"] = 1
            elif data[userid]["Race"] == "Fishman":
                data[userid]["Attributes"]["Strength"] = 2
                data[userid]["Attributes"]["Fortitude"] = 1
            else:
                data[userid]["Attributes"]["Fortitude"] = 2
                data[userid]["Attributes"]["Strength"] = 1
            
            data[userid]["Points"] = data[userid]["Level"] * 5 + 5
            
            profilesFile.seek(0)
            json.dump(data, profilesFile, indent=2)
            profilesFile.truncate()
            
            embed.description = f'Level: {data[userid]["Level"]}\nYou have {data[userid]["Points"]} points left to spend'
            embed.set_field_at(index=0, name='Strength', value=str({data[userid]["Attributes"]["Strength"]}), inline=False)
            embed.set_field_at(index=1, name='Fortitude', value=str({data[userid]["Attributes"]["Fortitude"]}), inline=False)
            embed.set_field_at(index=2, name='Agility', value=str({data[userid]["Attributes"]["Agility"]}), inline=False)
            embed.set_field_at(index=3, name='Luck', value=str({data[userid]["Attributes"]["Luck"]}), inline=False)
            
            StrengthButton.disabled = True if data[userid]["Points"] == 0 else False
            FortitudeButton.disabled = True if data[userid]["Points"] == 0 else False
            AgilityButton.disabled = True if data[userid]["Points"] == 0 else False
            LuckButton.disabled = True if data[userid]["Points"] == 0 else False
            
            resetButton.label = "Reset"
            resetButton.disabled = not any(item == "Fruit" for item in data[userid]["Inventory"])
            
            message = await callbackInteraction.followup.send(embed=discord.Embed(description="Stat points reset.", colour=discord.Colour.green()), ephemeral=True)
            await msg.edit(embed=embed, view=view)
            await asyncio.sleep(2)
            await callbackInteraction.followup.delete_message(message.id)
        
    StrengthButton.callback = callback
    FortitudeButton.callback = callback
    AgilityButton.callback = callback
    LuckButton.callback = callback
    
    resetButton.callback = reset
    
@tree.command(name='pay', description="Give another player money")
async def pay(interaction, amount: int, member: discord.Member):
    userid = interaction.user.id
    recieverid = member.id
    
    embedNoProfile = discord.Embed(description="Either the player you're trying to pay has no profile or the user has no profile.", colour=discord.Colour.red())
    embedNoMoney = discord.Embed(description="Not enough money.", colour=discord.Colour.red())
    embedSent = discord.Embed(description=f'Sent {amount} berries to {member.display_name}.', colour=discord.Colour.green())
    
    if not str(userid) in data or not str(recieverid) in data:
        await interaction.response.send_message(embed=embedNoProfile)
        return
    
    if data[str(userid)]["Money"] - amount < 0:
        await interaction.response.send_message(embed=embedNoMoney)
        return
    
    try:
        data[str(userid)]["Money"] -= amount
        data[str(recieverid)]["Money"] += amount
    
        profilesFile.seek(0)
        json.dump(data, profilesFile, indent=2)
        profilesFile.truncate()
        await interaction.response.send_message(embed=embedSent)
    except Exception:
        await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)
    
@tree.command(name='roll', description="Roll dice")
async def roll(interaction):
    if not str(interaction.user.id) in data:
        await interaction.response.send_message(f'You have no profile.', ephemeral=True, delete_after=3)
        return
    
    userid = str(interaction.user.id)
    luck = data[userid]["Attributes"]["Luck"]
    
    outcomes = list(range(1, 21))
    weight = [1 + luck/10] * 20
    
    roll = random.choices(outcomes, weights=weight, k=1)[0]
    
    embed = discord.Embed(description=f'{roll}', colour=discord.Colour.random())
    
    await interaction.response.send_message(embed=embed)
    
@tree.command(name='rolldmg', description="Roll damage")
async def rolldmg(interaction):
    if not str(interaction.user.id) in data:
        await interaction.response.send_message(f'You have no profile.', ephemeral=True, delete_after=3)
        return
    
    userid = str(interaction.user.id)
    strength = data[userid]["Attributes"]["Strength"]
    
    outcomes = list(range(1, 21))
    outcomes2 = list(range(1, 6))
    
    roll = random.choices(outcomes, k=1)[0]
    weakChance = random.choices(outcomes2, k=1)[0]
    
    modified_roll = round(roll * (1 + strength * 0.005))
    
    if weakChance == 1:
        embed = discord.Embed(description=f'{modified_roll}', colour=discord.Colour.random())
        await interaction.response.send_message(embed=embed)
        await interaction.followup.send(content=f'<:1_more:1203769624068497458>')
    else:
        embed = discord.Embed(description=f'{modified_roll}', colour=discord.Colour.random())
        await interaction.response.send_message(embed=embed)
        
    
@tree.command(name='npcrolldmg', description="Admin command")
async def npcrolldmg(interaction, member: discord.Member, maximum: int):
    if not str(member.id) in data:
        await interaction.response.send_message(f'You have no profile.', ephemeral=True, delete_after=3)
        return
    
    if interaction.user.id != 383895244686753802:
        await interaction.response.send_message("You do not have permission to use this command", ephemeral=True, delete_after=3)
        return
    
    userid = str(member.id)
    fortitude = data[userid]["Attributes"]["Fortitude"]
    
    outcomes = list(range(1, maximum+1))
    roll = random.choices(outcomes, k=1)[0]
    
    modified_roll = round(roll * (1 - fortitude * 0.005))
    
    try:
        data[userid]["Health"] = max(0, min(data[userid]["Health"] - modified_roll, 100))
        profilesFile.seek(0)
        json.dump(data, profilesFile, indent=2)
        profilesFile.truncate()
        
        embed = discord.Embed(description=f'{member.mention} took {modified_roll} damage.', colour=discord.Colour.random())
        
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)
    
@tree.command(name='unbiasedroll', description="Do an unbiased roll")
async def unbiasedroll(interaction):
    outcomes = list(range(1, 21))
    roll = random.choices(outcomes, k=1)[0]
    
    await interaction.response.send_message(embed=discord.Embed(description=f'{roll}', colour=discord.Colour.random()))

@app_commands.choices(type=[
    app_commands.Choice(name="Item", value="item"),
    app_commands.Choice(name="Money", value="money"),
    app_commands.Choice(name="Level", value="level"),
    app_commands.Choice(name="Attribute", value="attribute")
])
@tree.command(name='give', description="Admin command")
async def give(interaction, type: app_commands.Choice[str], member: str, object: str, num: int = None):
    if interaction.user.id != 383895244686753802:
        await interaction.response.send_message("You do not have permission to use this command", ephemeral=True, delete_after=3)
        return
    
    userList = member.split(" ")
    memberList = []
    
    for members in userList:
        newMember = re.sub(r'<@?(.*?)>', r'\1', members)    
        memberList.append(newMember)
    
    try:
        if type.value == "item":
            #data[str(member.id)]["Inventory"].append(object)
            for members in memberList:
                data[str(members)]["Inventory"].append(object)
            await interaction.response.send_message(embed=discord.Embed(description=f'Gave {userList} {object}', colour=discord.Colour.random()))
        elif type.value == "money":
            #data[str(member.id)]["Money"] += int(object)
            for members in memberList:
                data[str(members)]["Money"] += int(object)
            await interaction.response.send_message(embed=discord.Embed(description=f'Gave {userList} {object} Berries', colour=discord.Colour.random()))
        elif type.value == "level":
            #data[str(member.id)]["Level"] += int(object)
            #data[str(member.id)]["Points"] += (int(object) * 5)
            for members in memberList:
                data[str(members)]["Level"] += int(object)
                data[str(members)]["Points"] += (int(object) * 5)
            await interaction.response.send_message(embed=discord.Embed(description=f'Gave {userList} {object} level(s)', colour=discord.Colour.random()))
        elif type.value == "attribute":
            #data[str(member.id)]["Attributes"][object] += num
            for members in memberList:
                data[str(members)]["Attributes"][object] += num
            await interaction.response.send_message(embed=discord.Embed(description=f'{num} {object} points added to {userList}', colour=discord.Colour.random()))
    
        profilesFile.seek(0)
        json.dump(data, profilesFile, indent=2)
        profilesFile.truncate()
    except Exception as e:
        await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)
        print(e)

@tree.command(name='effect', description="Admin command")
async def effect(interaction, member: discord.Member, effect: str):
    if interaction.user.id != 383895244686753802:
        await interaction.response.send_message("You do not have permission to use this command", ephemeral=True, delete_after=3)
        return
    
    time = random.randint(10, 60)
    embed = discord.Embed(description=f'{effect} applied to {member.mention} for {time} seconds.', colour=discord.Colour.random())
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    
    await msg.pin()
    
    async def syncLoop():
        for i in range(time, 0, -1):
            embed.description = f'{effect} applied to {member.mention} for {i} seconds.'
            await msg.edit(embed=embed)
            await asyncio.sleep(1)
            
        if msg.pinned:
            await msg.unpin()
    
    asyncio.create_task(syncLoop())

@tree.command(name='profile', description="Check Profile")
async def profile(interaction, member: discord.Member = None):
    embedFailed = discord.Embed(description="Profile not found.", colour=discord.Colour.red())
    if member:
        if not str(member.id) in data:
            await interaction.response.send_message(embed=embedFailed)
            return
    else:
        if not str(interaction.user.id) in data:
            await interaction.response.send_message(embed=embedFailed)
            return
    
    embed = None
    
    if member:
        embed = discord.Embed(title=f'{member.display_name}\'s Profile', colour=discord.Colour.random())
        embed.set_footer(text=f'{member.id}')
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='Race:', value=f'{data[str(member.id)]["Race"]}', inline=True)
        embed.add_field(name='Level:', value=f'{data[str(member.id)]["Level"]}', inline=True)
        embed.add_field(name='Berries:', value=f'{data[str(member.id)]["Money"]}', inline=True)
        embed.add_field(name='Inventory:', value=None, inline=False)
        
        index = 0
        items = ""
        
        for item in data[str(member.id)]["Inventory"]:
            if item:
                items += f'\n{data[str(member.id)]["Inventory"][index]}'
                embed.set_field_at(index=3, name=f'Inventory:', value=f'{items}', inline=False)
                index += 1
    else:
        embed = discord.Embed(title=f'{interaction.user.display_name}\'s Profile', colour=discord.Colour.random())
        embed.set_footer(text=f'{interaction.user.id}')
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name='Race:', value=f'{data[str(interaction.user.id)]["Race"]}', inline=True)
        embed.add_field(name='Level:', value=f'{data[str(interaction.user.id)]["Level"]}', inline=True)
        embed.add_field(name='Berries:', value=f'{data[str(interaction.user.id)]["Money"]}', inline=True)
        embed.add_field(name='Inventory:', value=None, inline=False)
        
        index = 0
        items = ""
        
        for item in data[str(interaction.user.id)]["Inventory"]:
            if item:
                items += f'\n{data[str(interaction.user.id)]["Inventory"][index]}'
                embed.set_field_at(index=3, name=f'Inventory:', value=f'{items}', inline=False)
                index += 1
                
    await interaction.response.send_message(embed=embed)
   
@tree.command(name='shop', description="Show shop or buy items from it")
async def shop(interaction, buy: str = None):
    if not str(interaction.user.id) in data:
        await interaction.response.send_message(f'No profile', ephemeral=True, delete_after=3)
        return
    
    userid = str(interaction.user.id)
    
    if buy:
        if buy in shopData["Items"]:
            if data[userid]["Money"] > shopData["Items"][buy]:
                data[userid]["Inventory"].append(buy)
                data[userid]["Money"] -= shopData["Items"][buy]
                
                try:
                    profilesFile.seek(0)
                    json.dump(data, profilesFile, indent=2)
                    profilesFile.truncate()
                
                    await interaction.response.send_message(f'Successfully bought {buy}', ephemeral=True, delete_after=3)
                except Exception:
                    await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)
            else:
                await interaction.response.send_message(f'Not enough money.', ephemeral=True, delete_after=3)
        else:
            await interaction.response.send_message(f'Item isn\'t in shop', ephemeral=True, delete_after=3)
    else:
        embed=discord.Embed(title=f'Shop', description=f'Buy stuff!', colour=discord.Colour.orange())
        embed.set_thumbnail(url=f'https://cdn-icons-png.flaticon.com/512/513/513893.png')
        for item, value in shopData["Items"].items():
            if item:
                embed.add_field(name=f'{item}', value=f'{value:,}', inline=True)    
                
        await interaction.response.send_message(embed=embed)
            
@tree.command(name='damage', description="Admin command")
async def damage(interaction, member: discord.Member, amount: int):
    if not str(member.id) in data:
        await interaction.response.send_message("No Profile.", ephemeral=True, delete_after=3)
        return
        
    if interaction.user.id != 383895244686753802:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True, delete_after=3)
        return
        
    userid = str(member.id)
    fortitude = data[userid]["Attributes"]["Fortitude"]
        
    try:
        modified_amount = round(amount * (1 - fortitude * 0.005))
        data[userid]["Health"] = max(0, min(data[userid]["Health"] - modified_amount, 100))
        profilesFile.seek(0)
        json.dump(data, profilesFile, indent=2)
        profilesFile.truncate()
        await interaction.response.send_message(embed=discord.Embed(description=f'{member.mention} took {modified_amount} damage. {data[userid]["Health"]} / 100', colour=discord.Colour.random()))
    except Exception:
        await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)

@tree.command(name='heal', description="Admin command")
async def heal(interaction, member: discord.Member, amount: int):
    if not str(member.id) in data:
        await interaction.response.send_message("No Profile.", ephemeral=True, delete_after=3)
        return
        
    if interaction.user.id != 383895244686753802:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True, delete_after=3)
        return
        
    userid = str(member.id)
    
    try:
        data[userid]["Health"] = max(0, min(data[userid]["Health"] + amount, 100))
        profilesFile.seek(0)
        json.dump(data, profilesFile, indent=2)
        profilesFile.truncate()
        await interaction.response.send_message(embed=discord.Embed(description=f'Healed {member.mention} by {amount} HP.', colour=discord.Colour.random()))
    except Exception:
        await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)
    
@tree.command(name='healall', description="Admin command")
async def healall(interaction, amount: int):
    guild = interaction.user.guild
    error = False
    
    for member in guild.members:
        if str(member.id) in data and member.id != client.user.id:
            try:
                data[str(member.id)]["Health"] = max(0, min(data[str(member.id)]["Health"] + amount, 100))
                profilesFile.seek(0)
                json.dump(data, profilesFile, indent=2)
                profilesFile.truncate()
            except Exception:
                error = True
                
    if error:
        await interaction.response.send_message(content=f'Something went wrong, possibly healed some players.', ephemeral=True, delete_after=3)
    else:
        await interaction.response.send_message(embed=discord.Embed(description=f'All players were healed.', colour=discord.Colour.random()))

@tree.command(name='health', description="Show your character's health")
async def health(interaction, member: discord.Member = None):
    if member:
        if not str(member.id) in data:
            await interaction.response.send_message("No Profile.", ephemeral=True, delete_after=3)
            return
        else:
            userid = str(member.id)
            embed = discord.Embed(description=f'{data[userid]["Health"]} / 100', colour=discord.Colour.random())
            await interaction.response.send_message(embed=embed)
    else:
        if not str(interaction.user.id) in data:
            await interaction.response.send_message("No Profile.", ephemeral=True, delete_after=3)
            return
        else:
            userid = str(interaction.user.id)
            embed = discord.Embed(description=f'{data[userid]["Health"]} / 100', colour=discord.Colour.random())
            await interaction.response.send_message(embed=embed)
            
@tree.command(name='use', description='Use an item')
async def use(interaction, item: str):
    if not str(interaction.user.id) in data:
        await interaction.response.send_message("No Profile.", ephemeral=True, delete_after=3)
        return
    
    forbidden = ["Fruit"]
    
    if not item in data[str(interaction.user.id)]["Inventory"]:
        await interaction.response.send_message("You don't own this item.", ephemeral=True, delete_after=3)
    else:
        if item in forbidden:
            await interaction.response.send_message("You can't use this item.", ephemeral=True, delete_after=3)
        else:
            embed = discord.Embed(description=f'You used "{item}."', colour=discord.Colour.random())
            try:
                data[str(interaction.user.id)]["Inventory"].remove(item)
                profilesFile.seek(0)
                json.dump(data, profilesFile, indent=2)
                profilesFile.truncate()
                await interaction.response.send_message(embed=embed)
            except Exception:
                await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)
            
@tree.command(name='giveitem', description="Give a player an item from your inventory")
async def giveitem(interaction, member: discord.Member, item: str):
    if not str(interaction.user.id) in data or not str(member.id) in data:
        await interaction.response.send_message("No Profile.", ephemeral=True, delete_after=3)
        return
    
    if not item in data[str(interaction.user.id)]["Inventory"]:
        await interaction.response.send_message("You don't own this item.", ephemeral=True, delete_after=3)
    else:
        embed = discord.Embed(description=f'You gave {member.mention} {item}.', colour=discord.Colour.random())
        try:
            data[str(interaction.user.id)]["Inventory"].remove(item)
            data[str(member.id)]["Inventory"].append(item)
            profilesFile.seek(0)
            json.dump(data, profilesFile, indent=2)
            profilesFile.truncate()
            await interaction.response.send_message(embed=embed)
        except Exception:
            await interaction.response.send_message(content=f'Something went wrong.', ephemeral=True, delete_after=3)     

@tree.command(name='shopadd', description='Admin command')
async def shopadd(interaction, item: str, value: int):
    if interaction.user.id != 383895244686753802:
        await interaction.response.send_message(f'You don\'t have permission to use this command.', ephemeral=True, delete_after=3)
        return
    
    embed = discord.Embed(description=f'Added {item} to shop for {value:,} berries.', colour=discord.Colour.orange())
    
    try:
        shopData["Items"][item] = value
    
        shopFile.seek(0)
        json.dump(shopData, shopFile, indent=2)
        shopFile.truncate()
        
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message(content=f'Failed to add {item}', ephemeral=True, delete_after=3)
    
@tree.command(name='shopremove', description='Admin command')
async def shopadd(interaction, item: str):
    if interaction.user.id != 383895244686753802:
        await interaction.response.send_message(f'You don\'t have permission to use this command.', ephemeral=True, delete_after=3)
        return
    
    embed = discord.Embed(description=f'Removed {item} from shop', colour=discord.Colour.orange())
    
    try:
        shopData["Items"].pop(item)
    
        shopFile.seek(0)
        json.dump(shopData, shopFile, indent=2)
        shopFile.truncate()
        
        await interaction.response.send_message(embed=embed)
    except Exception:
        await interaction.response.send_message(content=f'Failed to remove {item}', ephemeral=True, delete_after=3)

client.run(settings["Token"])