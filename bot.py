# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 17:10:51 2022

TODO: I think Dabo is done - pending feedback from Night Shift.

- MOVE TO SLASH COMMANDS - SO EASY

- Ask Night Shift about item expiration dates, maybe?
- Consider making $my-inventory and $balance DM replies?

- Maybe replace all the nickname / member name checks with a simple function
def try_nick(user):
    if user.nick:
        return user.nick
    else:
        return user.name

Should make sure only channel accepted for commands is #dabo-tables
1019777894941212763

async def is_channel(ctx):   
    return ctx.channel.id == 1019777894941212763

@commands.check(is_channel)

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
    synced = await bot.tree.sync()
    print(str(len(synced)) + ' commands were synced.')

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
'''
@bot.command(name='remove-item')
@commands.has_role(admin_role)
@commands.guild_only()
async def remove_item(ctx, member: discord.Member, item):
    if ctx.author.nick:
        author = ctx.author.nick
    else:
        author = str(ctx.author)
    try:
        self_inventory[member.id].remove(item)
        message = discord.Embed(description = author + ' has removed ' + item + 
                                ' from ' + member.nick + '.',
                                color = discord.Color.light_grey())
    except:
        message = discord.Embed(description = 'Could not remove ' + item + 
                                ' from ' + member.nick + '.',
                                color = discord.Color.light_grey())
    await ctx.send(embed=message)
'''
@bot.command(name='clear-inventory')
@commands.has_role(admin_role)
@commands.guild_only()
async def clear_inventory(ctx, member: discord.Member):
    if ctx.author.nick:
        author = ctx.author.nick
    else:
        author = str(ctx.author)
    if member.nick:
        member_name = member.nick
    else:
        member_name = str(member)
    self_inventory[member.id] = []
    message = discord.Embed(description = author + ' has cleared ' + member_name +
                            '\'s inventory.',
                            color = discord.Color.light_grey())
    await ctx.send(embed=message)

@bot.command(name='save-data')
@commands.has_role(admin_role)
@commands.guild_only()
async def on_demand_save(ctx):
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

@bot.command(name='dabo')
@commands.has_any_role('Night Shift', 'Commander')
@commands.guild_only()
async def dabo(ctx):
    global dabo
    global wagers
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
    await ctx.send(embed=intro)
    await asyncio.sleep(dabo_duration)
    closed = discord.Embed(
        description = 'Betting is now closed! Play again next time!',
        color = discord.Color.red())
    dabo = False
    await ctx.send(embed=closed)
    collectWagers(wagers)
    result = spinWheel()
    delay = discord.Embed(
        description = 'Collecting wagers and spinning the wheel!',
        color = discord.Color.dark_gray())
    await ctx.send(embed=delay)
    message, payout = determineWinnings(result)
    await asyncio.sleep(random.randint(4,6))
    wheel1, wheel2, wheel3 = resultImages(result)
    await ctx.send(file = discord.File(wheel1))
    await asyncio.sleep(random.randint(2,4))
    await ctx.send(file = discord.File(wheel2))
    await asyncio.sleep(random.randint(5,7))
    await ctx.send(file = discord.File(wheel3))
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
    await ctx.send(embed=result)
    payWinners(payout, wagers)
    wagers = {}

@bot.command(name='wager')
@commands.guild_only()
async def wager(ctx, wager: int):
    global wagers
    if dabo == True:
        if ctx.author.nick:
            user = ctx.author.nick
        else:
            user = str(ctx.author)
        if dabo_min <= wager <= dabo_max:
            if verifyWager(ctx.author.id, wager):
                wagers[ctx.author.id] = wager
                message = (user + ', you wagered ' + str(wager) + 
                           ' ' + latinum + ' latinum. Good luck!')
                result_color = discord.Color.blue()
            else:
                message = ('Sorry, ' + user + 
                           ', you do not have enough latinum to make that wager...')
                result_color = discord.Color.red()
        else:
            message = ('Your bet has not been place. Bets must be at least ' 
                       + str(dabo_min) + ' and no more than '
                       + str(dabo_max) + '.')
            result_color = discord.Color.red()
    else:
        message = 'Sorry, the tables are closed at the moment.'
        result_color = discord.Color.light_gray()
    wager_result = discord.Embed(description = message, color = result_color)
    await ctx.send(embed=wager_result)

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

@bot.command(name='balance')
async def check_balance(ctx, member: discord.Member = None):
    if member:
        user_id = member.id
        if member.nick:
            user = member.nick
        else:
            user = str(member)
    else:
        user_id = ctx.author.id
        if ctx.author.nick:
            user = ctx.author.nick
        else:
            user = str(ctx.author)
    make_treasury_account(user_id)
    balance = treasury[user_id]
    message = (user + '\'s current balance is: ' + str(balance) + ' ' + 
               latinum + '.')
    response = discord.Embed(description = message, color = discord.Color.dark_gold())
    await ctx.send(embed=response)

@bot.command(name='shop-inventory')
@commands.guild_only()
async def inventory(ctx):
    message = discord.Embed(title = 'Shop Inventory',
                              description = 'Check out the amazing offerings below, ' +
                              'then use the command $buy "Item Name" to ' +
                              'purchase as many items as you can afford.\n' +
                              '----------',
                              color = discord.Color.blue())
    for item in shop_inventory:
        item_name = item + ': ' + str(shop_inventory[item]['price']) + ' ' + latinum
        item_description = shop_inventory[item]['description']
        message.add_field(name=item_name, value=item_description, inline=False)
    message.set_footer(text = 'Remember: all sales are final!')
    await ctx.send(embed=message)

@bot.command(name='my-inventory')
async def my_inventory(ctx):
    global self_inventory
    if ctx.author.nick:
        buyer = ctx.author.nick
    else:
        buyer = str(ctx.author)
    buyer_id = ctx.author.id
    buy_color = discord.Color.light_grey()
    make_item_inventory(buyer_id)
    if len(self_inventory[buyer_id]) > 0:
        message = discord.Embed(title = buyer + '\'s Inventory',
                                description = 'Here are your currently owned items. ' +
                                'Use some command Azure has not created yet to use your '+ 
                                'items.', color = buy_color)
        for item in self_inventory[buyer_id]:
            item_name = item
            item_description = shop_inventory[item]['description']
            message.add_field(name=item_name, value=item_description, inline=False)
    else:
        message = discord.Embed(title = buyer + '\'s Inventory',
                               description = 'You do not have any items yet. ' +
                               'Use the command $buy "Item Name" to start spending ' +
                               'your ' + latinum + '.')
    await ctx.send(embed=message)

@bot.command(name='buy')
@commands.guild_only()
async def buy_item(ctx, item):
    if item in shop_inventory:
        if ctx.author.nick:
            buyer = ctx.author.nick
        else:
            buyer = str(ctx.author)
        buyer_id = ctx.author.id
        buy_color = discord.Color.light_grey()
        make_treasury_account(buyer_id)
        if collectPayment(buyer_id, item):
            buy_message = buyer + ' has purchased ' + item + '.'
            disburseItem(buyer_id, item)
        else:
            buy_message = ('Sorry, ' + buyer + ', you do not have enough ' + latinum +
                           ' to make this purchase.')            
        message = discord.Embed(description = buy_message, color = buy_color)
        await ctx.send(embed=message)
    
@bot.command(name='stipend')
@commands.cooldown(1, 60*60*24, type = commands.BucketType.member)
@commands.guild_only()
async def stipend(ctx):
    if ctx.author.nick:
        user = ctx.author.nick
    else:
        user = str(ctx.author)
    user_id = ctx.author.id
    roles = [str(role) for role in ctx.author.roles]
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
    await ctx.send(embed=message)

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