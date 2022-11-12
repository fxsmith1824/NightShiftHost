# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 17:10:51 2022

TODO: 
- Ask Night Shift about item expiration dates, maybe?
- Consider making $my-inventory and $balance DM replies?

Should make sure only channel accepted for commands is #dabo-tables
1019777894941212763

async def is_channel(ctx):   
    return ctx.channel.id == 1019777894941212763

@commands.check(is_channel)

- Remember Dabo table open time is currently 10 seconds

@author: AzureRogue
"""

#%% Imports and Function Definitions

import nest_asyncio
nest_asyncio.apply()

import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import asyncio
import random
import pickle
import datetime

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)
admin_role = 'Night Shift'

dabo = False
wagers = {}
treasury = {}
shop_inventory = {}
self_inventory = {}

latinum = '<:mee6Coins:1017715720961925150>'
starting_balance = 500

@bot.event
async def on_ready():
    save_data.start()
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening,
                                  name='Faith of the Heart'))
    print(f'{bot.user.name} has connected to Discord!')
    #synced = await bot.tree.sync()
    #print(str(len(synced)) + ' commands were synced.')

@bot.command(name='sync')
@commands.dm_only()
async def sync_commands(ctx):
    synced = await bot.tree.sync()
    await ctx.send(content = str(len(synced)) + ' commands have been synced.')

def load_data():
    try:
        with open('data.pickle', 'rb') as file:
            treasury, shop_inventory, self_inventory = pickle.load(file)
        print('Successfully loaded data.')
    except:
        treasury = {295610445824393217: 1000,
                    104392361764737024: 9999}
        shop_inventory = {'Sample Item': {'price': 500, 
                                          'description': 'Just your usual item.'},
                          'Another Item': {'price': 250,
                                           'description': 'Cheaper item here.'}}
        self_inventory = {}
        print('Data failed to load - loading default test data.')
    return treasury, shop_inventory, self_inventory

def try_nick(user):
    if user.nick:
        return user.nick
    else:
        return user.name

@tasks.loop(minutes=10)
async def save_data():
    data_to_save = (treasury, shop_inventory, self_inventory)
    with open('data.pickle', 'wb') as file:
        pickle.dump(data_to_save, file)
    print('Data saved at ' + str(datetime.datetime.now()))
    print(treasury)

#%% Administrator Functions

@bot.tree.command(name='modify-latinum', description='Change the amount of ' +
                  'latinum a user has.')
@app_commands.checks.has_role(admin_role)
@app_commands.guild_only()
async def modify_latinum(interaction: discord.Interaction, member: discord.Member, amount: int):
    author_name = try_nick(interaction.user)
    member_name = try_nick(member)
    make_treasury_account(member.id)
    treasury[member.id] += amount
    message = discord.Embed(description = author_name + ' has give ' + member_name + 
                            ' ' + str(amount) + ' ' + latinum, 
                            color = discord.Color.dark_gold())
    await interaction.response.send_message(embed=message)

@bot.tree.command(name='remove-item', description='Remove an item from a user\'s ' +
                  'inventory.')
@app_commands.checks.has_role(admin_role)
@app_commands.guild_only()
async def remove_item(interaction: discord.Interaction, member: discord.Member, item: str):
    author_name = try_nick(interaction.user)
    member_name = try_nick(member)
    try:
        self_inventory[member.id].remove(item)
        message = discord.Embed(description = author_name + ' has removed ' + 
                                item + ' from ' + member_name + '.',
                                color = discord.Color.light_grey())
    except:
        message = discord.Embed(description = 'Could not remove ' + item + 
                                ' from ' + member_name + '.',
                                color = discord.Color.light_grey())
    await interaction.response.send_message(embed=message)

@bot.tree.command(name='clear-inventory', description='Remove all items from a ' +
                  'user\'s inventory.')
@app_commands.checks.has_role(admin_role)
@app_commands.guild_only()
async def clear_inventory(interaction: discord.Interaction, member: discord.Member):
    author_name = try_nick(interaction.user)
    member_name = try_nick(member)
    self_inventory[member.id] = []
    message = discord.Embed(description = author_name + ' has cleared ' + member_name +
                            '\'s inventory.', color = discord.Color.light_grey())
    await interaction.response.send_message(embed=message)

@bot.tree.command(name='save-data', description='Backup latinum balances and ' +
                  'personal inventories to bot host PC.')
@app_commands.checks.has_role(admin_role)
@app_commands.guild_only()
async def on_demand_save(interaction: discord.Interaction):
    await save_data()

#%% Dabo

dabo_min = 10
dabo_max = 1000
dabo_duration = 10

def spinWheel():
    shapes = ['circle', 'square' ,'triangle']
    counts = ['1', '2', '3']
    colors = ['red', 'green', 'blue']
    unique_shapes = ['quark-quark', 'ds9-ds9', 'ds9-ds9', 'ds9-ds9', 
                     'swirl-swirl', 'swirl-swirl', 'blackhole-blackhole',
                     'blackhole-blackhole', 'blackhole-blackhole']
    
    wheel = []
    inner_wheel = []
    
    for shape in shapes:
        for count in counts:
            for color in colors:
                item = count + '-' + color + '-' + shape
                item_2 = count + '-' + shape
                wheel.append(item)
                inner_wheel.append(item_2)
    
    wheel += unique_shapes
    inner_wheel += unique_shapes
    
    result = [random.choice(wheel), random.choice(wheel), random.choice(inner_wheel)]
    return result

def determineWinnings(result):
    uniques = ['swirl', 'quark', 'ds9', 'blackhole']
    counts = [x.split('-')[0] for x in result]
    if len([x.split('-') for x in result][1]) == 1:
        colors = [x.split('-') for x in result][1]
    else:
        colors = [x.split('-')[1] for x in result[:-1]]
    shapes = [x.split('-')[-1] for x in result]
    matches = {}
    matches['counts'] = (max(list({i:counts.count(i) for i in counts if i not in uniques}.values()) + [0]) +
                         counts.count('swirl'))
    matches['colors'] = (max(list({i:colors.count(i) for i in colors if i not in uniques}.values()) + [0]) +
                         colors.count('swirl'))
    matches['shapes'] = (max(list({i:shapes.count(i) for i in shapes if i not in uniques}.values()) + [0]) +
                         shapes.count('swirl'))
    if shapes.count('quark') == 3:
        message = 'DABO!!!'
        payout = 2000
    elif shapes.count('swirl') == 3:
        message = 'DABO!!'
        payout = 1000
    elif shapes.count('ds9') == 3:
        message = 'DABO!'
        payout = 150
    elif shapes.count('quark') == 2:
        message = 'Two Quarks!'
        payout = 5
    elif shapes.count('ds9') == 2:
        message = 'Two DS9s!'
        payout = 4
    elif matches['shapes'] == 3 and matches['colors'] == 2 and matches['counts'] == 3:
        message = 'Dabo!'
        payout = 10
    elif matches['counts'] == 3:
        message = 'Three of the same count!'
        payout = 2
    elif matches['shapes'] == 3:
        message = 'Three of the same shape!'
        payout = 1.5
    elif matches['colors'] == 2:
        message = 'Two of the same color.'
        payout = 0.2
    elif matches['counts'] == 2:
        message = 'Two of the same count.'
        payout = 0.15
    elif matches['shapes'] == 2:
        message = 'Two of the same shape.'
        payout = 0.1
    else:
        message = 'No winner this time... Try again!'
        payout = 0
    return message, payout

def verifyWager(userID, wager):
    if userID in treasury.keys():
        if treasury[userID] >= wager:
            return True
        else:
            return False
    else:
        treasury[userID] = 0
        return False

def collectWagers(wagers):
    for wager in wagers:
        treasury[wager] -= wagers[wager]

def payWinners(payout, wagers):
    for wager in wagers:
        treasury[wager] += int(wagers[wager]*payout)

def resultImages(result):
    image_folder = 'images'
    unique_shapes = ['quark-quark', 'ds9-ds9', 'ds9-ds9', 'ds9-ds9', 
                     'swirl-swirl', 'swirl-swirl']
    wheel1 = result[0]
    wheel2 = result[1]
    wheel3 = result[2]
    wheel1_file = os.path.join(image_folder, wheel1 + '.webp')
    wheel2_file = os.path.join(image_folder, wheel2 + '.webp')
    if wheel3 in unique_shapes:
        wheel3_file = os.path.join(image_folder, wheel3 + '-nc.webp')
    else:
        wheel3_file = os.path.join(image_folder, wheel3 + '.webp')
    return wheel1_file, wheel2_file, wheel3_file

@bot.tree.command(name='dabo', description = 'Start a game of dabo for the ' +
                  'whole server to bet on!')
@app_commands.checks.has_any_role('Night Shift', 'Commander')
@app_commands.guild_only()
async def dabo(interaction: discord.Interaction):
    global dabo
    global wagers
    channel = interaction.channel
    intro = discord.Embed(
        title = 'Play Some Dabo!',
        description = 'A game of Dabo is about to begin...',
        color = discord.Color.blue())
    intro.add_field(
        name = 'How to Play', value = 'Use the command \"$wager ' +
        '<integer>\" to bid <integer> ' + latinum +
        ' gold pressed latinum on the next spin!', inline = False)
    intro.add_field(
        name = 'Rules of the Game', value = 'Your wager must be ' +
        'at least ' + str(dabo_min) + ' and at most ' + str(dabo_max) +
        ' ' +latinum + ' to enter the game.\n' + 
        'Everyone wins or loses together, so ask the Blessed ' +
        'Exchequer for good luck!', inline = False)
    intro.set_footer(text = 'The tables will close in ' + str(dabo_duration) +
                     ' seconds.')
    dabo = True
    await interaction.response.send_message(embed=intro)
    await asyncio.sleep(dabo_duration)
    closed = discord.Embed(
        description = 'Betting is now closed! Play again next time!',
        color = discord.Color.red())
    dabo = False
    await channel.send(embed=closed)
    collectWagers(wagers)
    result = spinWheel()
    delay = discord.Embed(
        description = 'Collecting wagers and spinning the wheel!',
        color = discord.Color.dark_gray())
    await channel.send(embed=delay)
    message, payout = determineWinnings(result)
    await asyncio.sleep(random.randint(4,6))
    wheel1, wheel2, wheel3 = resultImages(result)
    await channel.send(file = discord.File(wheel1))
    await asyncio.sleep(random.randint(2,4))
    await channel.send(file = discord.File(wheel2))
    await asyncio.sleep(random.randint(5,7))
    await channel.send(file = discord.File(wheel3))
    await asyncio.sleep(1)
    if payout > 1:
        pay_color = discord.Color.gold()
    elif payout > 0:
        pay_color = discord.Color.light_grey()
    else:
        pay_color = discord.Color.dark_red()
    result = discord.Embed(title = message, color = pay_color,
                           description = 'The payout for this round is ' + 
                           str(payout) + 'x your wagers.')
    result.set_footer(text = 'Thank you for playing!')
    await channel.send(embed=result)
    payWinners(payout, wagers)
    wagers = {}

@bot.tree.command(name='wager', description='Place a bet on the ongoing game ' +
                  'of Dabo.')
@app_commands.guild_only()
async def wager(interaction: discord.Interaction, wager: int):
    global wagers
    if dabo == True:
        author_name = try_nick(interaction.user)
        if dabo_min <= wager <= dabo_max:
            if verifyWager(interaction.user.id, wager):
                wagers[interaction.user.id] = wager
                message = (author_name + ', you wagered ' + str(wager) + ' ' +
                           latinum + ' latinum. Good luck!')
                result_color = discord.Color.blue()
            else:
                message = ('Sorry, ' + author_name + ', you do not have enough ' +
                           'latinum to make that wager...')
                result_color = discord.Color.red()
        else:
            message = ('Your bet has not been place. Bets must be at least ' 
                       + str(dabo_min) + ' and no more than '
                       + str(dabo_max) + '.')
            result_color = discord.Color.red()
    else:
        message = 'Sorry, the tables are closed at the moment.'
        result_color = discord.Color.light_grey()
    wager_result = discord.Embed(description = message, color = result_color)
    await interaction.response.send_message(embed=wager_result)

#%% Latinum and Item Management

def make_treasury_account(user_id):
    if user_id not in treasury.keys():
        treasury[user_id] = starting_balance

def make_item_inventory(user_id):
    if user_id not in self_inventory.keys():
        self_inventory[user_id] = []

def collectPayment(buyer_id, item):
    if treasury[buyer_id] >= shop_inventory[item]['price']:
        treasury[buyer_id] -= shop_inventory[item]['price']
        return True
    else:
        return False

def disburseItem(buyer_id, item):
    make_item_inventory(buyer_id)
    self_inventory[buyer_id].append(item)

@bot.tree.command(name='balance', description='Check your (or another users\'s) ' +
                  'current latinum balance.')
async def check_balance(interaction: discord.Interaction, member: discord.Member = None):
    if member:
        user_id = member.id
        user = try_nick(member)
        private = False
    else:
        user_id = interaction.user.id
        user = try_nick(interaction.user)
        private = True
    make_treasury_account(user_id)
    balance = treasury[user_id]
    message = (user + '\'s current balance is: ' + str(balance) + ' ' + 
               latinum + '.')
    response = discord.Embed(description = message, color = discord.Color.dark_gold())
    await interaction.response.send_message(embed=response, ephemeral=private)

@bot.tree.command(name='shop-inventory', description='Check what items are currently ' +
                  'available for purchase.')
@app_commands.guild_only()
async def inventory(interaction: discord.Interaction):
    message = discord.Embed(title = 'Shop Inventory',
                              description = 'Check out the amazing offerings below, ' +
                              'then use the command /buy to ' +
                              'purchase as many items as you can afford.\n' +
                              '----------',
                              color = discord.Color.blue())
    for item in shop_inventory:
        item_name = item + ': ' + str(shop_inventory[item]['price']) + ' ' + latinum
        item_description = shop_inventory[item]['description']
        message.add_field(name=item_name, value=item_description, inline=False)
    message.set_footer(text = 'Remember: all sales are final!')
    await interaction.response.send_message(embed=message)

@bot.tree.command(name='my-inventory', description='See what items are in your ' +
                  'inventory.')
async def my_inventory(interaction: discord.Interaction):
    global self_inventory
    user = try_nick(interaction.user)
    user_id = interaction.user.id
    buy_color = discord.Color.light_grey()
    make_item_inventory(user_id)
    if len(self_inventory[user_id]) > 0:
        message = discord.Embed(title = user + '\'s Inventory',
                                description = 'Here are your currently owned items. ' +
                                'Use some command Azure has not created yet to use your '+ 
                                'items.', color = buy_color)
        for item in self_inventory[user_id]:
            item_name = item
            item_description = shop_inventory[item]['description']
            message.add_field(name=item_name, value=item_description, inline=False)
    else:
        message = discord.Embed(title = user + '\'s Inventory',
                               description = 'You do not have any items yet. ' +
                               'Use the command /buy to start spending ' +
                               'your ' + latinum + '.')
    await interaction.response.send_message(embed=message, ephemeral=True)

@bot.tree.command(name='buy', description='Purchase an item from the shop ' + 
                  '(/shop-inventory).')
@app_commands.guild_only()
async def buy_item(interaction: discord.Interaction, item: str):
    if item in shop_inventory:
        buyer = try_nick(interaction.user)
        buyer_id = interaction.user.id
        buy_color = discord.Color.light_grey()
        make_treasury_account(buyer_id)
        if collectPayment(buyer_id, item):
            buy_message = buyer + ' has purchased ' + item + '.'
            disburseItem(buyer_id, item)
        else:
            buy_message = ('Sorry, ' + buyer + ', you do not have enough ' 
                           + latinum + ' to make this purchase.')  
        message = discord.Embed(description = buy_message, color = buy_color)
        await interaction.response.send_message(embed=message)

@bot.tree.command(name='stipend', description='Collect your daily stipend.')
@app_commands.checks.cooldown(1, 60*60*24)
@app_commands.guild_only()
async def stipend(interaction: discord.Interaction):
    user = try_nick(interaction.user)
    user_id = interaction.user.id
    roles = [str(role) for role in interaction.user.roles]
    make_treasury_account(user_id)
    base_payout = 100
    if 'Commander' in roles:
        rank = 'Commander'
        payout = base_payout + 25
    elif 'Lt. Commander' in roles:
        rank = 'Lt. Commander'
        payout = base_payout + 15
    elif 'Lieutenant' in roles:
        rank = 'Lieutenant'
        payout = base_payout + 5
    elif 'Ensign' in roles:
        rank = 'Ensign'
        payout = base_payout
    else:
        payout = base_payout - 75
    treasury[user_id] += payout
    text = ('For reaching the rank of ' + rank + ', ' + user + ' has been granted ' 
            + str(payout) + ' ' + latinum + ' for their daily stipend.')
    message = discord.Embed(description = text, color = discord.Color.dark_gold())
    await interaction.response.send_message(embed=message)
    
@stipend.error
async def stipend_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        if error.retry_after > 3600:
            retry_time = round(error.retry_after/3600, 1)
            retry_unit = 'hours'
        elif error.retry_after > 60:
            retry_time = int(error.retry_after/60)
            retry_unit = 'minutes'
        else:
            retry_time = int(error.retry_after)
            retry_unit = 'seconds'
        text = ('You cannot collect another stipend yet. Try again in ' 
                + str(retry_time) + ' ' + retry_unit + '.')
        message = discord.Embed(description = text, color = discord.Color.light_grey())
        await ctx.send(embed=message)

#%% RUN BOT, RUN
treasury, shop_inventory, self_inventory = load_data()
bot.run(token)